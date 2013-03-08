import logging
import urlparse

from .backends import OpenLock, RedisLock

BACKEND = 'redis://'
DEFAULT_TIMEOUT = 60
DEFAULT_EXPIRES = 10
KEY_PREFIX = 'pylock:'
BACKEND_CLASSES = [OpenLock, RedisLock]


logger = logging.getLogger('pylock')


class Lock(object):
    """
    Distributed locking.

    Usage::

        with Lock('my_lock'):
            print "Critical section"

    :param  key:        The key against which the lock will be held.
    :param  expires:    We consider any existing lock older than
                        ``expires`` seconds to be invalid in order to
                        detect crashed clients. This value must be higher
                        than it takes the critical section to execute.
    :param  timeout:    If another client has already obtained the lock,
                        sleep for a maximum of ``timeout`` seconds before
                        giving up. A value of 0 means no wait (give up
                        right away).

    """
    def __init__(self, key, expires=None, timeout=None, backend=None):
        if backend is None:
            backend = BACKEND
        if expires is None:
            expires = DEFAULT_EXPIRES
        if timeout is None:
            timeout = DEFAULT_TIMEOUT
        # Figure out which lock backend to use (default to OpenLock)
        backend_class = BACKEND_CLASSES[0]
        for backend_class in BACKEND_CLASSES:
            if backend.startswith(backend_class.NAME):
                break
        logger.info("Using {0} lock backend".format(backend_class.NAME))
        key = "{0}{1}".format(KEY_PREFIX, key)
        connection_info = parse(backend)
        client = backend_class.get_client(**connection_info)
        self._lock = backend_class(key, expires, timeout, client)

    def __enter__(self):
        self._lock.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._lock.release()


def parse(url):
    """Parses a distributed lock backend URL."""
    # Register extra schemes in URLs.
    for backend in BACKEND_CLASSES:
        urlparse.uses_netloc.append(backend.NAME)

    url = urlparse.urlparse(url)

    # Remove query strings.
    path = url.path[1:]
    path = path.split('?', 2)[0]

    # Update with environment configuration.
    connection_info = {
        'db': path,
        'user': url.username,
        'password': url.password,
        'host': url.hostname,
        'port': url.port
    }

    return connection_info
