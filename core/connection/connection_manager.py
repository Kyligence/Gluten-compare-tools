from core.common import config


class ConnectionManager(object):
    def __init__(self):
        self.urls = config.DEST_URLS
