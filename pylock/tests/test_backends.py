import unittest
import time

import redis

from nose.tools import raises
from nose.tools import eq_
from mock import Mock
from mock import patch


class TestRedisLock(unittest.TestCase):
    def _makeOne(self):
        from pylock import DEFAULT_EXPIRES, DEFAULT_TIMEOUT
        from pylock.backends.redis_lock import RedisLock

        # wrap the RedisLock backend in a context manager to be able to test it
        class Lock(RedisLock):
            def __init__(self, key, expires=DEFAULT_EXPIRES, timeout=DEFAULT_TIMEOUT, client=None):
                super(Lock, self).__init__(key, expires, timeout, client)

            def __enter__(self):
                self.acquire()

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.release()
        return Lock

    def _lockException(self):
        from pylock import LockTimeout
        return LockTimeout

    def test_redis_sub(self):
        mock_redis = Mock(spec=redis.Redis)

        def test_it():
            lock = self._makeOne()
            with lock('somekey', client=mock_redis):
                val = 2 + 4
        test_it()
        method_names = [x[0] for x in mock_redis.method_calls]
        eq_(method_names[0], 'setnx')
        eq_(method_names[1], 'expire')
        eq_(method_names[2], 'delete')
        eq_(len(method_names), 3)

    def test_nocontention(self):
        mock_redis = Mock(spec=redis.Redis)

        def test_it():
            lock = self._makeOne()
            with lock('somekey', client=mock_redis):
                val = 2 + 4
        test_it()
        method_names = [x[0] for x in mock_redis.method_calls]
        eq_(method_names[0], 'setnx')
        eq_(method_names[1], 'expire')
        eq_(method_names[2], 'delete')
        eq_(len(method_names), 3)

    def test_nocontention_and_no_lock_delete(self):
        mock_redis = Mock(spec=redis.Redis)
        mock_time = Mock()
        vals = [35, 0, 0, 0]
        mock_time.side_effect = lambda: vals.pop()

        @patch('time.time', mock_time)
        def test_it():
            lock = self._makeOne()
            with lock('somekey', expires=30, client=mock_redis):
                val = 2 + 4
        test_it()
        method_names = [x[0] for x in mock_redis.method_calls]
        eq_(method_names[0], 'setnx')
        assert 'delete' not in method_names

    def test_contention_and_someone_else_replacing_timeout(self):
        mock_redis = Mock(spec=redis.Redis)
        mock_time = Mock()
        vals = [35, 0, 0, 0]
        mock_time.side_effect = lambda: vals.pop()
        mock_redis.get.return_value = False
        mock_redis.setnx.return_value = False
        timeout = self._lockException()

        @raises(timeout)
        @patch('time.time', mock_time)
        @patch('time.sleep', Mock())
        def test_it():
            lock = self._makeOne()
            with lock('somekey', expires=30, timeout=0, client=mock_redis):  # pragma: nocover
                val = 2 + 4
        test_it()
        method_names = [x[0] for x in mock_redis.method_calls]
        eq_(method_names[0], 'setnx')
        eq_(len(method_names), 2)

    def test_contention(self):
        mock_redis = Mock(spec=redis.Redis)
        mock_redis.get.return_value = 150
        mock_redis.getset.return_value = 150
        mock_redis.setnx.return_value = False

        def test_it():
            lock = self._makeOne()
            with lock('somekey', client=mock_redis):
                val = 2 + 4
        test_it()
        eq_(len(mock_redis.method_calls), 5)
        setnx, get = mock_redis.method_calls[:2]
        eq_(setnx[1][0], 'somekey')
        eq_(get[1][0], 'somekey')

    def test_timeout_current_val_is_newer(self):
        mock_redis = Mock(spec=redis.Redis)
        mock_redis.setnx.return_value = False
        mock_redis.get.return_value = time.time() + 200
        timeout = self._lockException()
        mock_time = Mock()
        mock_time.return_value = 0

        array = []

        @raises(timeout)
        @patch('time.sleep', mock_time)
        def test_it():
            lock = self._makeOne()
            with lock('somekey', timeout=1, client=mock_redis):
                array.append(4)  # pragma: nocover
        test_it()
        eq_(len(array), 0)

    def test_timeout_no_current_value_and_mock_redis(self):
        mock_redis = Mock(spec=redis.Redis)
        mock_redis.setnx.return_value = False
        mock_redis.get.return_value = 150
        mock_redis.getset.return_value = False
        timeout = self._lockException()
        mock_time = Mock()
        mock_time.return_value = 0

        array = []

        @raises(timeout)
        @patch('time.sleep', mock_time)
        def test_it():
            lock = self._makeOne()
            with lock('somekey', timeout=1, client=mock_redis):
                array.append(4)  # pragma: nocover
        test_it()
        eq_(len(array), 0)

    def test_get_client(self):
        from pylock.backends.redis_lock import RedisLock
        db = 4
        host = '33.33.33.10'
        port = '1234'
        password = 'cookies'
        with patch('pylock.backends.redis_lock.StrictRedis') as mock_redis:
            RedisLock.get_client(db=db, host=host, port=port, password=password)
            mock_redis.assert_called_once_with(host, port, db, password)

    def test_get_client_default_connection_values(self):
        from pylock.backends.redis_lock import RedisLock
        db = None
        host = None
        port = None
        password = None
        with patch('pylock.backends.redis_lock.StrictRedis') as mock_redis:
            RedisLock.get_client(db=db, host=host, port=port, password=password)
            mock_redis.assert_called_once_with('localhost', 6379, 0, None)
