class LockTimeout(BaseException):
    """Raised in the event a timeout occurs while waiting for a lock"""


class BaseLock(object):
    def __init__(self, key, expires, timeout, client):
        """
        :param  client:      The the backend client instance to use.

        """
        self.key = key
        self.expires = expires
        self.timeout = timeout
        self.client = client

    @classmethod
    def get_client(cls, **connection_args):
        raise NotImplementedError

    def acquire(self):
        raise NotImplementedError

    def release(self):
        raise NotImplementedError
