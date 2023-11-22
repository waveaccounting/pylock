import logging
import time

from redis import StrictRedis
from redis.backoff import ExponentialBackoff
from redis.retry import Retry

from importlib import import_module, util as import_util

from .. import BaseLock, LockTimeout

logger = logging.getLogger("pylock")


class RedisLock(BaseLock):
    url_schemes = ['redis', 'rediss']

    connection = None

    @classmethod
    def get_client(cls, **connection_args):
        from pylock import DJANGO_REDIS_CACHE_NAME, USE_DJANGO_REDIS_CACHE

        if not cls.connection:
            if USE_DJANGO_REDIS_CACHE:
                cache_name = DJANGO_REDIS_CACHE_NAME or "default"
                if import_util.find_spec("django_redis") is None:
                    raise ModuleNotFoundError("django_redis is not installed")
                module = import_module("django_redis")
                cls.connection = module.get_redis_connection(cache_name)
                logger.info(f"redis connection from django cache client. cache_name: {cache_name}")
            else:
                host = connection_args.get('host') or 'localhost'
                port = connection_args.get('port') or 6379
                password = connection_args.get('password')
                db = connection_args.get('db') or 0
                ssl = connection_args.get('ssl') or False
                retry = Retry(ExponentialBackoff(cap=10, base=1), 25)
                errors_to_retry = [ConnectionError, TimeoutError, ConnectionResetError]
                cls.connection = StrictRedis(host, port, db, password, ssl=ssl, retry=retry,
                                             retry_on_error=errors_to_retry, health_check_interval=20)
                logger.info("redis connection initialized by StrictRedis")

        return cls.connection

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
