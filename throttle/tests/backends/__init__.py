from throttle.backends.base import ThrottleBackendBase
from .test_get_backend import test_get_backend


class TestThrottleBackend(ThrottleBackendBase):
    pass


__all__ = ['test_get_backend']
