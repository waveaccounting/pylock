
PYLOCK_BACKEND = 'memcached://host:port/'

PYLOCK_BACKEND = 'redis://:password@host:port/db'
# all fields after the scheme are optional, and will default to localhost on port 6379, using database 0.

PYLOCK_BACKEND = 'open://local'

PYLOCK_DEFAULT_TIMEOUT = 60

PYLOCK_EXPIRES = 10

PYLOCK_KEY_PREFIX = 'pylock:'


Redis

https://chris-lamb.co.uk/posts/distributing-locking-python-and-redis


Memcache

https://github.com/snbuback/DistributedLock
http://jbq.caraldi.com/2010/08/simple-distributed-lock-with-memcached.html
http://www.regexprn.com/2010/05/using-memcached-as-distributed-locking.html



TODO:
 - better handle redis/memcache connection issues