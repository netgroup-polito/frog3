from paste.evalexception.middleware import limit

__author__ = 'Alberto Geniola'

import sys
import signal
import os
import hashlib
import time
import logging
import time
import datetime
import json
import MySQLdb as mdb
from novaclient import client as Novaclient
from glanceclient import client as Glanceclient
from keystoneclient.v2_0 import client as Keystoneclient
from compute_service import CacheManagerConfig as cm
import CacheImg
import Utils
import InvalidImageException

DEF_PART_SUFFIX = ".precache_part"
DEF_PENDING_FILE = "pending.json"

class CacheManager:
    """ Cache Management Class """

    def __init__(self, base_path=None, mysql_host=None, mysql_user=None, mysql_pass=None, mysql_db=None, hostname=None,
                 nova_version=None, username=None, password=None, tenant=None, auth_url=None, image_timeout=86400,
                 diskquota=None,enable_md5_checking=False):
        # Todo: check auth success, check we got admin power, check configuration
        if not os.path.isdir(base_path):
            raise Exception("Given basepath is not valid.")
        else:
            self.basepath = base_path

        if not os.access(base_path, os.W_OK):
            raise Exception("Given basepath is not writeable fot the current user.")

        self.image_timeout = image_timeout
        self.nova = Novaclient.Client(nova_version, username, password, tenant, auth_url)
        self.keystone = Keystoneclient.Client(username=username, password=password, tenant_name=tenant,
                                              auth_url=auth_url)
        self.hostname = hostname
        self.mysqlhost = mysql_host
        self.mysqluser = mysql_user
        self.mysqlpass = mysql_pass
        self.mysqldb = mysql_db
        self.diskquota = diskquota
        self._last_poll_res = []
        self.enable_md5_checking = enable_md5_checking

        self.pending_downloads = []
        # TODO: Check image deletion has been disabled from nova.conf in order to avoid conflicts and race conditions.

    def _handle_previous_fail(self):
        # Check if there's some pending state
        pending_file_path = os.path.join(self.basepath, DEF_PENDING_FILE)
        if not os.path.isfile(pending_file_path):
            return
        try:
            with open(pending_file_path) as data_file:
                data = json.load(data_file)
                for r in data:
                    image_id = r[0]
                    part_file = r[1]
                    logger.info(msg="Image id %s has not been downloaded correctly. Setting error and deleting its part file (%s)." % (image_id, part_file))
                    self._set_error(image_id, "Service error: download failed.")
                    os.unlink(part_file)
            os.unlink(pending_file_path)
        except:
            # I know, I shouldn't, but this is a prototype.
            pass

    def _persist_fail(self):
        logger.info(msg="persisting pending downloads...")
        pending_file_path = os.path.join(self.basepath, DEF_PENDING_FILE)
        json.dump(self.pending_downloads, open(pending_file_path, 'wb'))

    def _get_used_images(self):
        """
        This methods gets a list of server from the nova-controller and lists only images needed to the current node.
        :return: A list of used images used on this compute node
        """
        used_images = []
        # Look for all used images for current node
        for srv in self.nova.servers.list():
            # Note: we need to have admin credentials to get this parameter!
            srvhost = getattr(srv, "OS-EXT-SRV-ATTR:host")
            if srvhost == self.hostname:
                used_images.append(srv.image)
        # If a given image is attached to a local server, we shouldn't remove it
        return used_images

    def _notify_image_removed(self, imageid):
        db = mdb.connect(host=self.mysqlhost, user=self.mysqluser, passwd=self.mysqlpass, db=self.mysqldb)
        c = db.cursor()
        c.execute(
            """DELETE FROM prefetching WHERE compute_hostname=%s AND image_id=%s AND marked_for_deletion=1 ORDER BY priority ASC""",
            (self.hostname, imageid))
        db.commit()
        db.close()

    def list_all(self):
        """
        This method queries the DB and returns a full list of all images regarding this current node.
        :return: a list of CacheImg regarding this compute-node
        """
        res = []
        db = mdb.connect(host=self.mysqlhost, user=self.mysqluser, passwd=self.mysqlpass, db=self.mysqldb)
        c = db.cursor()
        c.execute(
            """SELECT compute_hostname, image_id, md5, status, priority, marked_for_deletion, message  FROM prefetching WHERE compute_hostname=%s ORDER BY priority ASC""",
            (self.hostname))
        for i in range(c.rowcount):
            row = c.fetchone()
            img = CacheImg.CacheImg(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
            res.append(img)
        db.close()
        return res

    def check_local_image_hash(self, imageid, md5):
        """
        This method will look for the corresponding local imageid given and will hash it using
        MD5. The result is then checked against given MD5 digest.
        :param imageid: imageid of the local image to check
        :param md5: digest to check local image against
        :return: True if the digest of the local image corresponds to the given md5 parameter
        """

        # Skip this if it has been disable
        if not self.enable_md5_checking:
            logger.debug(msg="Skipping image check because of ENABLE_MD5_CHECKING=False in the configuration file.")
            return True

        # Calculating file name requires SHA1 hash
        localimg = hashlib.sha1(imageid).hexdigest()

        h = hashlib.md5()
        with open(os.path.join(self.basepath, localimg), 'rb') as file:
            # loop till the end of the file
            chunk = 0
            while chunk != b'':
                # read only 1024 bytes at a time
                chunk = file.read(1024)
                h.update(chunk)

        if h.hexdigest() != md5:
            logger.info("check_local_image_hash on image %s returned %s. Should match %s" % (imageid,h.hexdigest(),md5))

        return h.hexdigest() == md5

    def _set_image_cached(self, image_id):
        db = mdb.connect(host=self.mysqlhost, user=self.mysqluser, passwd=self.mysqlpass, db=self.mysqldb)
        c = db.cursor()
        c.execute(
            """UPDATE prefetching SET status='CACHED', dowload_completed_on=NOW() WHERE compute_hostname=%s AND image_id=%s""",
            (self.hostname, image_id))
        db.commit()
        db.close()

    def handle_base_image_prefetch(self, cacheimage):
        """
        Handles a single image prefetch request. In other words, it will simply handle all the records of the prepache table
        that have marked_for_deletion=0 (i.e. not to be removed).
        :param cacheimage:
        :return:
        """

        if cacheimage.marked_for_deletion:
            # Let's only check that the image marked for deletion is present in our cache. If it is not, notify the error
            present = False
            if not self.is_img_in_cache(cacheimage.image_id):
                logger.info(
                    msg="Image %s has been found on DB but it's not yet present into local cache. Ignoring..." % cacheimage.image_id)
                self._set_error(cacheimage.image_id,
                                "Image %s has been found on DB but it's not yet present into local cache. Ignoring..." % cacheimage.image_id)
            else:
                logger.info(
                    msg="Image %s has been marked for deletion. No need to handle its prefetch request." % cacheimage.image_id)

            return

        if cacheimage.status.upper() == 'PENDING':
            # Before downloading the image, let's check nova hasn't already cached the image
            if self.is_img_in_cache(cacheimage.image_id):
                logger.debug(msg="Image %s is already cached locally. Checking its MD5 DIGEST..." % cacheimage.image_id)
                # Are those image equals?
                if self.check_local_image_hash(cacheimage.image_id, cacheimage.md5):
                    logger.debug(
                        msg="Image %s is OK, we assume it's already cached locally. Updating DB." % cacheimage.image_id)
                    self._set_image_cached(cacheimage.image_id)
                else:
                    logger.debug(msg="ERROR! Image %s is INCONSISTENT, please check!" % cacheimage.image_id)
                    self._set_error(cacheimage.image_id,
                                    "The image is already present on client, but its checksum mismatches. Please correct the error manually.")
            else:
                logger.info(msg="Image %s is going to be downloaded." % cacheimage.image_id)
                try:
                    self.prefetch_image(cacheimage.image_id)
                except InvalidImageException:
                    self._set_error(cacheimage.image_id, "Invalid image-id.")

        elif cacheimage.status.upper() == 'DOWNLOADING':
            logger.info(msg="Skipping image %s because it's still being downloaded" % cacheimage.image_id)

        elif cacheimage.status.upper() == 'CACHED':
            if not self.check_local_image_hash(cacheimage.image_id, cacheimage.md5):
                logger.info(msg="ERROR! Image %s is INCONSISTENT, please check!" % cacheimage.image_id)

    def _set_error(self, imgid, message):
        # Notify the central DB we are downloading the image
        db = mdb.connect(host=self.mysqlhost, user=self.mysqluser, passwd=self.mysqlpass, db=self.mysqldb)
        c = db.cursor()
        c.execute("""UPDATE prefetching SET status='ERROR', message=%s WHERE compute_hostname=%s AND image_id=%s""",
                  (message, self.hostname, imgid))
        db.commit()
        # We close the DB.
        db.close()


    def prefetch_image(self, imgid):
        """
        This method will download the image. Upon end, the central DB will be notified about the download result.
        :param img: The image id corresponding to the image to download and prefetch
        :return:
        """

        # Get the image data as an iterable data object
        gclient = self._get_glance_client()
        # Make sure there's enough local space for thi image
        size = gclient.images.get(imgid).size / (1024 * 1024)

        if size >= self.get_available_space():
            logger.warning(msg="There's no space to precache image %s. Needed %s mb, left %s mb."
                            % (imgid, str(size), str(self.get_available_space())))
            self._set_error(imgid, "There's no space for this image to be cached on this node.")
            return

        dstfilepath = hashlib.sha1(imgid).hexdigest()
        dstfilepath = os.path.join(self.basepath, dstfilepath)
        partfilepath = dstfilepath + DEF_PART_SUFFIX

        skip_download = False

        # If the wanted image is already present in cache, check its checksum. If it's ok, simply set the CACHED status on the server.
        # If not, notify the error.
        if os.path.isfile(dstfilepath):
            logger.warning("File %s already exists in image base directory. Checking hash..." % dstfilepath)
            checksum = gclient.images.checksum(imgid)
            corrupted = self.check_local_image_hash(imgid,checksum)
            if corrupted:
                logger.warning("Checksum on image id %s (file %d) mismatches. User action is required." % (imgid, dstfilepath))
                self._set_error(imgid, "Checksum mismatches. User action is required.")
                return
            else:
                logger.info("Checksum ok on image id %s (file %d). Skipping download ... " % (imgid, dstfilepath))
                skip_download = True

        if not skip_download:
            pending_item = (imgid, partfilepath)
            self.pending_downloads.append(pending_item)
            self._persist_fail()

            download_start_time = datetime.datetime.now()
            data = gclient.images.data(imgid)

            # Notify the central DB we are downloading the image
            db = mdb.connect(host=self.mysqlhost, user=self.mysqluser, passwd=self.mysqlpass, db=self.mysqldb)
            c = db.cursor()
            c.execute("""UPDATE prefetching SET status='DOWNLOADING' WHERE compute_hostname=%s AND image_id=%s""",
                      (self.hostname, imgid))
            db.commit()
            # We close the DB. The download process might take a lot of time.
            #db.close()

            # Download and write
            updatethreshold = 0.05*len(data)
            step = 0
            total = 0
            out_file = open(partfilepath, "wb")
            for buff in data:
                out_file.write(buff)
                step = step + len(buff)
                total = total + len(buff)
                if step > updatethreshold:
                    logstr = "{:10.2f}".format(float(float(total)*100/float(len(data)))) + "% completed"
                    c.execute("""UPDATE prefetching SET status='DOWNLOADING', message=%s WHERE compute_hostname=%s AND image_id=%s""",
                      (logstr, self.hostname, imgid))
                    logger.info(msg=logstr)
                    db.commit()
                    step = 0
            out_file.close()
            download_finish_time = datetime.datetime.now()
            lapsed = download_finish_time - download_start_time
            finish_time_str = "Download finished in " + "{:10.2f}".format(lapsed.total_seconds()) + " seconds. "
            c.execute(
                """UPDATE prefetching SET message=%s WHERE compute_hostname=%s AND image_id=%s""",
                (finish_time_str, self.hostname, imgid))
            db.commit()

            # It may happen that nova has downloaded the image while this thread was performing the download of that image.
            # So we double check here. If an image is found, we trust its checksum is ok and we don't overwrite it. The cleaner will
            # detect any problem when running next time.
            if os.path.isfile(dstfilepath):
                logger.warning("Nova has cached the image %s (file %s) while I was still downloading it. I won't overwrite that image. Part file will be deleted." % (imgid, dstfilepath))
                os.unlink(partfilepath)
            else:
                os.rename(partfilepath, dstfilepath)
            logger.info(msg="Image %s has been downloaded." % imgid)

        # Notify we've finished
        c.execute(
            """UPDATE prefetching SET status='CACHED', dowload_completed_on=NOW() WHERE compute_hostname=%s AND image_id=%s""",
            (self.hostname, imgid))
        db.commit()

        db.close()

        self.pending_downloads.remove(pending_item)
        self._persist_fail()


    def is_img_in_cache(self, toCheck):
        """
        Checks if the given imageid has already been cached locally. Note that the parameter should be
        an image-id, which will be sha1ed and checked against the files present into the local cache.
        :param toCheck: the imageid to verify.
        :return: True if the given image has already been cached locally, False otherwise.
        """
        for f in os.listdir(self.basepath):
            if f == hashlib.sha1(toCheck).hexdigest():
                return True
        return False

    def _get_glance_client(self):
        """
        :return:a glance client object to be used to deal with Glance service.
        """
        glanceid = None
        # Retrieve the glance service ID
        for srv in self.keystone.services.list():
            if srv.type == "image":
                glanceid = srv.id
                break
        if glanceid == None:
            raise Exception("Cannot find any image service!")

        glanceendpoint = None
        # Retrieve the glance service endpoint
        for ep in self.keystone.endpoints.list():
            if ep.service_id == glanceid:
                glanceendpoint = ep.internalurl
                break

        if glanceendpoint == None:
            raise Exception("Serviceid %s has no registered endpoint on keystone." % glanceid)

        gclient = Glanceclient.Client(version=1, endpoint=glanceendpoint, token=self.keystone.auth_token)
        return gclient

    def _is_imagefile_old_enough(self, base_file):
        mtime = os.path.getmtime(base_file)
        age = time.time() - mtime
        return age > self.image_timeout

    def get_available_space(self):
        return min(self.diskquota, Utils.get_free_disk_space(self.basepath))

    def poll_db(self):
        imgs = self.list_all()

        if imgs is None:
            imgs = []

        imgs.sort(key=lambda x: x.image_id, reverse=True)

        #logger.info("last poll: %s" % self._last_poll_res)
        #logger.info("current poll: %s" % imgs)

        if len(imgs) != len(self._last_poll_res):
            self._last_poll_res = imgs
            return True

        for i in range(0, len(imgs)):
            if imgs[i].image_id != self._last_poll_res[i].image_id:
                self._last_poll_res = imgs
                return True
            if imgs[i].md5 != self._last_poll_res[i].md5:
                self._last_poll_res = imgs
                return True
            if imgs[i].status != self._last_poll_res[i].status:
                self._last_poll_res = imgs
                return True
            if imgs[i].marked_for_deletion != self._last_poll_res[i].marked_for_deletion:
                self._last_poll_res = imgs
                return True
        return False

    def _run_cleaner(self):
        """
        Warning! This is not thread safe!!
        This method takes care of clearing the local cache. Here's how it works
        1. Loop over all the image files into basepath
        2. For each one, check if it still under usage.
            If so, don't delete it.
            If not in use:
                check if it has been marked for deletion. If so, delete it directly, without checking it's age.
                If the image isn't marked for deletion, delete it only if it's old enough.
        :return:
        """
        logger.info(msg="Running cleaner")

        all_images = self.list_all()
        in_use = self._get_used_images()

        # For each image into the basepath directory, if the image is not in use and has not to be cached and it's old enough,
        # delete it.
        for localfile in os.listdir(self.basepath):
            if len(localfile) != 40:
                # Only take in account hash-like files.
                continue
            # Is the file in use?
            inuse = False
            id_in_use = None
            for i in in_use:
                if hashlib.sha1(i['id']).hexdigest() == localfile:
                    inuse = True
                    id_in_use = i['id']
                    break
            if inuse:
                logger.info(
                    msg="Skipping imageid %s (local %s ) because it's under usage." % (id_in_use, localfile))
            else:
                # Check if the current image is included into the cache-enabled images. If so, handle it here. We need to reverse SHA1 to check their ID
                iscacheable = False
                for cachable in all_images:
                    if hashlib.sha1(cachable.image_id).hexdigest() == localfile:
                        # Ok, the image was in our resident cache list. Delete it only if it has been marked for deletion
                        # or if it's old enough to be removed.
                        iscacheable = True
                        if cachable.marked_for_deletion:
                            logger.info(
                                msg="Removing Local Image %s (file %s) because it's been marked for deletion." %
                                    (cachable.image_id, localfile))
                            os.remove(os.path.join(self.basepath, localfile))
                            self._notify_image_removed(cachable.image_id)
                        else:
                            logger.info(
                                msg="Skipping Local Image %s (file %s) because it's in resident cache." %
                                    (cachable.image_id, localfile))

                        # Image found, no need to iterate again
                        break;

                # All cacheable images have been handled before.
                if iscacheable:
                    continue

                # Otherwise only the images that are neither not in use or not in resident cache are left.
                # Remove them if old enough. This basically implements the same Nova Cache policy.
                if self._is_imagefile_old_enough(os.path.join(self.basepath, localfile)):
                    logger.info(msg="Local Image %s is old enough and it's going to be deleted." % localfile)
                    os.remove(os.path.join(self.basepath, localfile))
                else:
                    logger.debug(msg="Local Image %s is not old enough to be deleted." % localfile)

mngref = None
def main(argv):
    try:
        signal.signal(signal.SIGTERM, sigterm_handler)

        if os.getuid() != 0:
            raise Exception("This scripts must run as ROOT.")

        conf = None
        conffile = None
        if (len(argv) > 1):
            conffile = argv[1]

        if conffile is None:
            conf = cm.CacheManagerConfig()
        else:
            conf = cm.CacheManagerConfig(conffile)

        # Setup the logging file
        handler = logging.FileHandler(conf.log_file)

        level = logging.getLevelName(conf.log_level)
        handler.setLevel(level)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        logger.info("CacheManager started!")

        manager = CacheManager(base_path=conf.basepath,
                               mysql_host=conf.mysqlhost,
                               mysql_user=conf.mysqluser,
                               mysql_pass=conf.mysqlpass,
                               mysql_db=conf.mysqldb,
                               hostname=conf.hostname,
                               nova_version=conf.novaversion,
                               username=conf.username,
                               password=conf.password,
                               tenant=conf.tenant,
                               auth_url=conf.auth_url,
                               image_timeout=conf.image_timeout,
                               diskquota=conf.diskquota,
                               enable_md5_checking=conf.enable_md5_checking)

        CacheManager.mngref = manager
        # sleep time in case of network absence
        crash_sleep_time = 30
        # Time for DB polling
        db_poll_interval = conf.db_poll_interval
        # Every 200 db polling, run anyway (so cleaner has a chance to do its job)
        count = 0
        maxcount = 200
        # Daemonize: poll the server and run only if something regarding this node has changed.
        while True:
            try:
                manager._handle_previous_fail()
                change_happend = manager.poll_db()
                if change_happend or count == maxcount:
                    count = 0
                    logger.info(msg="DB has new info for me. Runing tasks.")

                    # It's worth to first run the cleaner in order to free space (if possible)
                    manager._run_cleaner()

                    """ Synch the local cache with the remote DB:"""
                    all_images = manager.list_all()
                    for img in all_images:
                        manager.handle_base_image_prefetch(img)
                time.sleep(db_poll_interval)
                count = count + 1
            except Exception:
                logger.error(msg='Unexpected exception. ', exc_info=True)
                logger.warning(msg='Execution will be restarted in %s' % str(crash_sleep_time))
                manager._persist_fail()
                time.sleep(crash_sleep_time)
    except Exception:
        manager._persist_fail()
        logger.info(msg="Cache manager crashed.")
        logger.critical(msg='Unexpected exception. ', exc_info=True)
        return 1

def sigterm_handler(_signo, _stack_frame):
    CacheManager.mngref._persist_fail()
    logger.warning("SIGTERM received. Exiting.")
    sys.exit(0)

# Very start configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Main Hook
if __name__ == "__main__":
    main(sys.argv)