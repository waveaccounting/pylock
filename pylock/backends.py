import time
from redis import StrictRedis


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


class OpenLock(BaseLock):
    NAME = 'open'

    @classmethod
    def get_client(cls, **connection_args):
        return None

    def acquire(self):
        return True

    def release(self):
        return True


class RedisLock(BaseLock):
    NAME = 'redis'

    @classmethod
    def get_client(cls, **connection_args):
        host = connection_args.get('host', 'localhost')
        port = connection_args.get('port', 6379)
        password = connection_args.get('password')
        db = connection_args.get('db', 0)
        return StrictRedis(host, port, db, password)

    def __init__(self, key, expires, timeout, client):
        super(RedisLock, self).__init__(key, expires, timeout, client)
        self.start_time = time.time()

    def acquire(self):
        redis = self.client
        timeout = self.timeout
        while timeout >= 0:
            expires = time.time() + self.expires + 1

            if redis.setnx(self.key, expires):
                # We gained the lock; enter critical section
                self.start_time = time.time()
                redis.expire(self.key, int(self.expires))
                return

            current_value = redis.get(self.key)

            # We found an expired lock
            if current_value and float(current_value) < time.time():
                # Nobody raced us to replacing it
                if redis.getset(self.key, expires) == current_value:
                    self.start_time = time.time()
                    redis.expire(self.key, int(self.expires))
                    return

            timeout -= 1
            if timeout >= 0:
                time.sleep(1)
        raise LockTimeout("Timeout while waiting for lock")

    def release(self):
        redis = self.client
        # Only delete the key if we completed within the lock expiration,
        # otherwise, another lock might have been established
        if time.time() - self.start_time < self.expires:
            redis.delete(self.key)
