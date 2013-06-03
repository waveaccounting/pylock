import unittest

from nose.tools import eq_
from mock import Mock

from pylock.backends.open_lock import OpenLock
from pylock.backends.redis_lock import RedisLock


class TestLock(unittest.TestCase):
    def setUp(self):
        import pylock
        self.current_settings = (pylock.DEFAULT_BACKEND, pylock.DEFAULT_EXPIRES, pylock.DEFAULT_TIMEOUT, pylock.KEY_PREFIX)

    def tearDown(self):
        import pylock
        (pylock.DEFAULT_BACKEND, pylock.DEFAULT_EXPIRES, pylock.DEFAULT_TIMEOUT, pylock.KEY_PREFIX) = self.current_settings

    def test_open_backend_is_properly_detected(self):
        import pylock
        pylock.DEFAULT_BACKEND = {'class': 'pylock.backends.open_lock.OpenLock', 'connection': 'open://'}
        lock = pylock.Lock('somekey')
        self.assertEqual(lock._lock.__class__, OpenLock)

    def test_redis_backend_is_properly_detected(self):
        import pylock
        pylock.DEFAULT_BACKEND = {'class': 'pylock.backends.redis_lock.RedisLock', 'connection': 'redis://'}
        lock = pylock.Lock('somekey')
        self.assertEqual(lock._lock.__class__, RedisLock)

    def test_default_values_are_used(self):
        import pylock
        pylock.DEFAULT_BACKEND = {'class': 'pylock.backends.open_lock.OpenLock', 'connection': 'open://'}
        pylock.DEFAULT_EXPIRES = 999
        pylock.DEFAULT_TIMEOUT = 888
        pylock.KEY_PREFIX = 'cookies-are-us-'
        lock = pylock.Lock('somekey')
        expected_key = "cookies-are-us-somekey"
        self.assertEqual(lock._lock.key, expected_key)
        self.assertEqual(lock._lock.expires, 999)
        self.assertEqual(lock._lock.timeout, 888)

    def test_context_manager_calls_backend_methods(self):
        import pylock
        lock = pylock.Lock('somekey')
        lock._lock = Mock()

        def test_it():
            with lock:
                val = 2 + 4

        test_it()

        # The context manager should call the lock backend's acquire method on entry and the release method
        # on exit
        method_names = [x[0] for x in lock._lock.method_calls]
        eq_(method_names[0], 'acquire')
        eq_(method_names[1], 'release')
        eq_(len(method_names), 2)

    def test_lock_is_released_on_exception(self):
        import pylock
        lock = pylock.Lock('somekey')
        lock._lock = Mock()

        def test_it():
            with lock:
                raise Exception()

        try:
            test_it()
        except Exception:
            pass

        # The context manager should call the lock backend's acquire method on entry and the release method
        # when the exception is raised
        method_names = [x[0] for x in lock._lock.method_calls]
        eq_(method_names[0], 'acquire')
        eq_(method_names[1], 'release')
        eq_(len(method_names), 2)
