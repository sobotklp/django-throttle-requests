from base import ThrottleBackendBase
from django.core import cache

class CacheBackend(ThrottleBackendBase):
    def test_limit(self, strategy, timestamp, *args, **kwargs):
        pass
