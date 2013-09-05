Usage
-----

::

    from pylock import Lock

    with Lock('a_key', expires=60, timeout=10):
        # do something that should only be done one at a time

Configuration
-------------

Backends
~~~~~~~~

There are three available backends:

Open (non-locking) backend
^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    DEFAULT_BACKEND = {
        'class': 'pylock.backends.open_lock.OpenLock',
        'connection': 'open://'
    }

**Warning** This backend is not a real lock since it can always be
acquired even if another instance has acquired it already. It is meant
to be used for testing when you don't want to depend on a running redis
or memcache instance and don't care about the lock working.

Redis backend
^^^^^^^^^^^^^

::

    DEFAULT_BACKEND = {
        'class': 'pylock.backends.redis_lock.RedisLock',
        'connection': 'redis://'
    }

Note: all fields after the scheme are optional, and will default to
localhost on port 6379, using database 0.

Memcache backend (coming soon)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``DEFAULT_TIMEOUT`` (default: 60)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If another client has already obtained the lock, sleep for a maximum of
this many seconds before giving up. A value of 0 means no wait (give up
right away).

The default timeout can be overridden when instantiating the lock.

``DEFAULT_EXPIRES`` (default: 10)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We consider any existing lock older than this many seconds to be invalid
in order to detect crashed clients. This value must be higher than it
takes the critical section to execute.

The default expires can be overridden when instantiating the lock.

``KEY_PREFIX`` (default ``'pylock:'``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is used to prefix the key for the generated lock.

For ``Lock('somekey')``, the generated key will be ``'pylock:somekey'``

Inspired by
-----------

Redis backend
~~~~~~~~~~~~~

The redis backend is almost an exact copy of Ben Bangert's
```retools.lock`` <https://github.com/bbangert/retools/blob/master/retools/lock.py>`_
which is based on `Chris Lamb's
example <https://chris-lamb.co.uk/posts/distributing-locking-python-and-redis>`_

Memcache backend (coming soon)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The memcache backend is inspired by the following: -
https://github.com/snbuback/DistributedLock -
http://jbq.caraldi.com/2010/08/simple-distributed-lock-with-memcached.html
-
http://www.regexprn.com/2010/05/using-memcached-as-distributed-locking.html

TODO: - better handle redis/memcache connection issues
