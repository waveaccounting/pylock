from .. import BaseLock


class OpenLock(BaseLock):
    url_scheme = 'open'

    @classmethod
    def get_client(cls, **connection_args):
        return None

    def acquire(self):
        return True

    def release(self):
        return True
