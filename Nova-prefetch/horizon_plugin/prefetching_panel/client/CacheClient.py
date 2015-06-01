__author__ = 'Alberto Geniola'
import sys
import os
import CacheClientConfig
import MySQLdb as mdb
from prefetching_panel import CacheImg


CM_CLIENT_CONFIG = "CM_CLIENT_CONFIG"

def _list(config, hostname=None, status=None):
        res = []
        db = mdb.connect(host=config.mysqlhost,user=config.mysqluser,passwd=config.mysqlpass,db=config.mysqldb)
        c = db.cursor()

        if (hostname is not None) and (status is not None):
            c.execute("""SELECT compute_hostname, image_id, md5, status, priority, marked_for_deletion, message FROM prefetching WHERE compute_hostname=%s AND status=%s""", (hostname, status))
        elif (hostname is None) and (status is not None):
            c.execute("""SELECT compute_hostname, image_id, md5, status, priority, marked_for_deletion, message FROM prefetching WHERE status=%s""", (status))
        elif (hostname is not None) and (status is None):
            c.execute("""SELECT compute_hostname, image_id, md5, status, priority, marked_for_deletion, message FROM prefetching WHERE compute_hostname=%s""", (hostname))
        elif (hostname is None) and (status is None):
            c.execute("""SELECT compute_hostname, image_id, md5, status, priority, marked_for_deletion, message FROM prefetching""")

        for i in range(c.rowcount):
            row = c.fetchone()
            img = CacheImg.CacheImg(row[0],row[1],row[2],row[3],row[4],row[5],row[6])
            res.append(img)

        db.close()
        return res


def _delete(config, hostname, image_id):
    # if the remote image is in pending or error status, just remove it.
    # if it's in other status, simply enable it's marked_for_deletion flag
    db = mdb.connect(host=config.mysqlhost,user=config.mysqluser,passwd=config.mysqlpass,db=config.mysqldb)
    c = db.cursor()
    c.execute("""UPDATE prefetching SET marked_for_deletion=1 WHERE status<>'PENDING' AND compute_hostname=%s AND image_id=%s""", (hostname, image_id))
    db.commit()
    c.execute("""DELETE FROM prefetching WHERE (status='PENDING' || status='ERROR') AND compute_hostname=%s AND image_id=%s""", (hostname, image_id))
    db.commit()
    db.close()


def _add(config, hostname, image_id, checksum):
    # if the remote image is in pending or error status, just remove it.
    # if it's in other status, simply enable it's marked_for_deletion flag
    db = mdb.connect(host=config.mysqlhost,user=config.mysqluser,passwd=config.mysqlpass,db=config.mysqldb)
    c = db.cursor()
    c.execute("""INSERT INTO prefetching(compute_hostname, image_id, md5, added_on) VALUES(%s,%s,%s,NOW())""", (hostname, image_id, checksum))
    db.commit()
    db.close()

def print_usage():
    print ""
    print "Usage:"
    print ""
    print "cacheclient [--config <config_file.conf>] <command> [CMD OPTIONS]"
    print ""
    print "if the --config parameter is omitted, environment variable " + CM_CLIENT_CONFIG + " will be used instead."
    print ""
    print "COMMANDS"
    print "\tlist  \tList all the cache information stored into the central DB. You may want to filter results by "
    print "\t      \tspecifying --host <hostname> or --status <status>"
    print "\tdelete\tDelete a specific image from the caching directory of a specific compute node. Requires "
    print "\t      \t--host <hostname> and --image_id <imageid> parameters"
    print "\tadd   \tQueues a given image (specified by --image_id) to a particular compute node (specified by --host)"
    print "\t      \tThis command also requires a --checksum <digest> argument, so the server will be able to perform"
    print "\t      \timage checks and validation. If you are unsure about the image checksum, please run "
    print "\t      \tglance image-show <image-id>"
    print "\t      \tand look for the checksum property."
    print ""
    print "This utility is provided as is, without any warranty. For any information, please contact albertogeniola@gmail.com"
    print "Developed by Alberto Geniola (April 2015)"


def cmd_list(config, opts=None):
    host = None
    status = None

    if opts is not None:
        for i in xrange(0, len(opts),2):
            if opts[i] == "--host":
                if len(opts) <= (i+1):
                    raise SyntaxError(opts[i]+" option requires a value")
                else:
                    host = opts[i+1]
            elif opts[i] == "--status":
                if len(opts) <= (i+1):
                    raise SyntaxError(opts[i]+" option requires a value")
                else:
                    status = opts[i+1]
            else:
                raise SyntaxError("Invalid option: " + opts[i])

    imgs = _list(config,hostname=host, status=status)

    print "{0:<16} {1:^40} {2:^10} {3:^40} {4:>32}".format("HOST", "IMAGE-ID", "STATUS", "MESSAGE", "HASH")
    for img in imgs:
        if img.status == "ERROR":
            print '\033[91m' + "{0:16} {1:^40} {2:^10} {3:^40} {4:32}".format(img.compute_host, img.image_id, img.status, img.message, img.md5) + '\033[0m'
        else:
            print "{0:16} {1:^40} {2:^10} {3:^40} {4:32}".format(img.compute_host, img.image_id, img.status, img.message, img.md5)


def cmd_delete(config, opts=None):
    host = None
    image_id = None

    if opts is None:
        raise SyntaxError("Command DELETE requires --host and --image_id parameters.")

    if len(opts) != 4:
        raise SyntaxError("Invalid syntax. Expecting --host <host> --image_id <imageid>.")

    for i in xrange(0, len(opts), 2):
        if opts[i] == "--host":
            if len(opts) <= (i+1):
                raise SyntaxError(opts[i]+" option requires a value")
            else:
                host = opts[i+1]
        elif opts[i] == "--image_id":
            if len(opts) <= (i+1):
                raise SyntaxError(opts[i]+" option requires a value")
            else:
                image_id = opts[i+1]
        else:
            raise SyntaxError("Invalid option: " + opts[i])

    if host is None or image_id is None:
        raise SyntaxError("Invalid syntax. Expecting --host <host> --image_id <imageid>.")

    # Ok, now perform deletion:
    _delete(config, host, image_id)


def cmd_add(config, opts=None):
    host = None
    image_id = None
    checksum = None

    if opts is None:
        raise SyntaxError("Command ADD requires --host, --image_id and --checksum parameters.")

    if len(opts) != 6:
        raise SyntaxError("Invalid syntax. Expecting --host <host> --image_id <imageid> --checksum <checksum>")

    for i in xrange(0, len(opts), 2):
        if opts[i] == "--host":
            if len(opts) <= (i+1):
                raise SyntaxError(opts[i]+" option requires a value")
            else:
                host = opts[i+1]
        elif opts[i] == "--image_id":
            if len(opts) <= (i+1):
                raise SyntaxError(opts[i]+" option requires a value")
            else:
                image_id = opts[i+1]
        elif opts[i] == "--checksum":
            if len(opts) <= (i+1):
                raise SyntaxError(opts[i]+" option requires a value")
            else:
                checksum = opts[i+1]
        else:
            raise SyntaxError("Invalid option: " + opts[i])

    if host is None or image_id is None:
        raise SyntaxError("Invalid syntax. Expecting --host <host> --image_id <imageid>.")

    # Ok, now perform deletion:
    _add(config, host, image_id, checksum)


def execute_command(config, args):
    opts = None
    if len(args) > 1:
        opts = args[1::]

    if args[0] == "list":
        cmd_list(config, opts)
    elif args[0] == "delete":
        cmd_delete(config, opts)
    elif args[0] == "add":
        cmd_add(config, opts)
    else:
        raise SyntaxError("Unrecognized command: "+args[0])


def main(args):
    # Argument checking
    confFile = None
    startIndex=1
    if len(args) < 2:
        print_usage()
        return

    if args[1] != "--config":
        # Check if an environment variable is available
        startIndex=1
        f = os.environ.get(CM_CLIENT_CONFIG)
        if f is None or not os.path.isfile(f):
            print "Invalid configuration file given " + f
            print_usage()
            return 1
        else:
            confFile = f
    else:
        # If the conf file has been explicity set, use that one
        startIndex=3
        if not os.path.isfile(args[2]):
            print "Invalid configuration file given " + args[2] + "."
            print_usage()
            return 1
        else:
            confFile = args[2]

    # Now parse the config file provided and setup the configuration
    try:
        config = CacheClientConfig.CacheManagerConfig(confFile)
    except:
        print "There was an error while parsing the configuration file. Please check the Exception details."
        raise

    if startIndex >= len(args):
        print "Missing command."
        print_usage()
        return

    try:
        execute_command(config, args[startIndex::])
    except SyntaxError:
        info, info2, info3 = sys.exc_info()
        print info2
        print_usage()
        return
    except:
        info, info2, info3 = sys.exc_info()
        print info
        print info2
        print info3
        return


# Main Hook
if __name__ == "__main__":
    main(sys.argv)