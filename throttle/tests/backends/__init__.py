from throttle.backends.base import ThrottleBackendBase

class TestThrottleBackend(ThrottleBackendBase):
    pass

from .test_get_backend import test_get_backend
__all__ = ['test_get_backend']