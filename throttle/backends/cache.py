from base import RateLimitBackendBase
from django.core import cache

class CacheBackend(RateLimitBackendBase):
    def test_limit(self, strategy, timestamp, *args, **kwargs):
        pass
