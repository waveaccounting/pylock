from importlib import import_module
import logging
import urlparse

from .backends import LockTimeout

DEFAULT_TIMEOUT = 60
DEFAULT_EXPIRES = 10
KEY_PREFIX = 'pylock:'
DEFAULT_BACKEND = {
    'class': 'pylock.backends.redis_lock.RedisLock',
    'connection': 'redis://'
}


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
    def __init__(self, key, expires=None, timeout=None, backend_class_path=None, backend_connection=None):
        if expires is None:
            expires = DEFAULT_EXPIRES
        if timeout is None:
            timeout = DEFAULT_TIMEOUT
        if backend_class_path is None:
            backend_class_path = DEFAULT_BACKEND['class']
        if backend_connection is None:
            backend_connection = DEFAULT_BACKEND['connection']
        # Load backend class
        backend_class = get_backend_class(backend_class_path)
        logger.info("Using {0} lock backend".format(backend_class.__name__))
        key = "{0}{1}".format(KEY_PREFIX, key)
        connection_info = parse(backend_connection, url_scheme=backend_class.url_scheme)
        client = backend_class.get_client(**connection_info)
        self._lock = backend_class(key, expires, timeout, client)

    def __enter__(self):
        self._lock.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._lock.release()


class ImproperlyConfigured(Exception):
    pass


def get_backend_class(import_path):
    try:
        dot = import_path.rindex('.')
    except ValueError:
        raise ImproperlyConfigured("%s isn't a pylock backend module." % import_path)
    module, classname = import_path[:dot], import_path[dot+1:]
    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing pylock backend module %s: "%s"' % (module, e))
    try:
        return getattr(mod, classname)
    except AttributeError:
        raise ImproperlyConfigured('Pylock backend module "%s" does not define a "%s" class.' % (module, classname))


def parse(url, url_scheme):
    """Parses a distributed lock backend URL."""
    # Register extra schemes in URLs.
    urlparse.uses_netloc.append(url_scheme)

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
