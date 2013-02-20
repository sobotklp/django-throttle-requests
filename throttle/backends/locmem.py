import threading

from base import ThrottleBackendBase

class LocMemBackend(ThrottleBackendBase):
    """
    A backend that uses the server's local memory to store throttling buckets

    This backend is not intended to be used for production purposes.
    """
    def test_limit(self, strategy, timestamp, *args, **kwargs):
        pass

