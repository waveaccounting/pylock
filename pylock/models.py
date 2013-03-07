from . import BACKEND, DEFAULT_TIMEOUT, DEFAULT_EXPIRES, KEY_PREFIX

# Try to load values from Django settings if available
try:
    from django.conf import settings
    BACKEND = settings.get('PYLOCK_BACKEND', BACKEND)
    DEFAULT_TIMEOUT = settings.get('PYLOCK_DEFAULT_TIMEOUT', DEFAULT_TIMEOUT)
    DEFAULT_EXPIRES = settings.get('PYLOCK_DEFAULT_EXPIRES', DEFAULT_EXPIRES)
    KEY_PREFIX = settings.get('PYLOCK_KEY_PREFIX', KEY_PREFIX)
except ImportError:
    pass
