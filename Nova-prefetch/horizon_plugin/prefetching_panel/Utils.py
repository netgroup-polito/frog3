__author__ = 'webking'

from openstack_dashboard.prefetching_panel.client import CacheClientConfig as cclientconf
from openstack_dashboard.prefetching_panel.client import CacheClient as cclient
from openstack_dashboard import api


def get_user_hosts(request):
    """
    Returns only ompute nodes list
    :return:
    """
    res = []
    hosts = api.nova.host_list(request)
    for h in hosts:
        if h.service == u'compute':
            res.append(h)

    return res


def add_image_to_cache(request, hostname, imageid):
    # Retrieve image checksum
    img = api.glance.image_get(request,imageid)
    checksum = img.checksum
    cclient._add(get_cclient_config(), hostname, imageid, checksum)


def remove_image_from_precache(request, hostname, imageid):
    cclient._delete(get_cclient_config(), hostname, imageid)


def get_cclient_config():
    config = cclientconf.CacheManagerConfig("openstack_dashboard/prefetching_panel/caching.conf")
    return config


def get_available_images_for_host(request, host):
    res = []
    # Get all the records regarding the given host
    host_records = cclient._list(get_cclient_config(), hostname=host, status=None)

    # Get all available images for this user
    visible_images = api.glance.image_list_detailed(request,paginate=False)[0]


    for i in visible_images:
        found = False
        for r in host_records:
            if i.id == r.image_id:
                found = True
                break
        if not found:
            res.append((i.id, i.name))

    return res


def get_user_hosts_and_images(request):

    # Get all info from DB
    all_records = cclient._list(get_cclient_config(), hostname=None, status=None)

    visible_hosts = get_user_hosts(request)
    visible_images = api.glance.image_list_detailed(request,paginate=False)[0]

    # Filter all images the current user can see
    images = filter_by_current_user(all_records, visible_images, visible_hosts)

    return visible_hosts, images


def get_images_list(request):
    res = []
    visible_images =  api.glance.image_list_detailed(request,paginate=False)[0]
    for i in visible_images:
        el = (i.id, i.name)
        res.append(el)
    return res


def get_hosts_list(request):
    hosts, images = get_user_hosts_and_images(request)
    res = []
    for h in hosts:
        res.append((h.host_name,h.host_name))
    return res


def filter_by_current_user(all_records, visible_images, visible_hosts):
    """
    Given an array of CacheImg records, this function will filter all results
    through the visible_images arg and the visible hosts arg. This is a workaround
    to implement a simple security and isolation layer, which it's not yet compliant
    with OS standards, but it's a start.
    """
    result = []

    for r in all_records:
        visible = False
        # look into visible_images
        for vi in visible_images:
            if r.image_id == vi.id:
                # Trick: assign also the image name
                r.image_name = vi.name
                visible = True
                break
        if visible:
            visible = False
            for vh in visible_hosts:
                if vh.host_name == r.compute_host:
                    visible = True
                    break
        if visible:
            result.append(r)

    return result


class NodeWrapper:
    def __init__(self,hostname):
        self.hostname = hostname
        self.images = []

    def append_img(self,img):
        self.images.append(img)

    def get_images(self):
        return self.images

    def id(self):
        return self.hostname
