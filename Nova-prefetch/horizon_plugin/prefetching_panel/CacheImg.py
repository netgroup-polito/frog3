__author__ = 'webking'


class CacheImg:
    _compute_host=None
    _image_id = None
    _md5 = None
    _status = None
    _priority = None
    _marked_for_deletion = None
    _message = None
    _image_name = None

    def __init__(self, compute_host, image_id, md5, status, priority, deletion_marked, message):
        self._compute_host = compute_host
        self._image_id = image_id
        self._md5 = md5
        self._status = status
        self._priority = priority
        self._marked_for_deletion = deletion_marked
        self._message = message

    def id(self):
        return self._compute_host+"_"+self._image_id

    @property
    def compute_host(self):
        return self._compute_host

    @property
    def image_id(self):
        return self._image_id

    @property
    def md5(self):
        return self._md5

    @property
    def status(self):
        if self._marked_for_deletion and self._status != 'ERROR':
            return 'PENDING DELETION'
        else:
            return self._status

    @property
    def priority(self):
        return self._priority

    @property
    def marked_for_deletion(self):
        return self._marked_for_deletion == 1

    @property
    def message(self):
        return self._message

    @property
    def image_name(self):
        """
        If the image name has been set it will be returned. Otherwise the image-id is returned.
        :return:
        """
        if self._image_name is None:
            return self._image_id
        else:
            return self._image_name
