from base import ThrottleBackendBase
from django.core.cache import get_cache, cache

class CacheBackend(ThrottleBackendBase):
    def test_limit(self, zone_name, bucket_key, bucket_num, *args, **kwargs):
        bucket_cache_key = "%s:%s:%s" % (zone_name, bucket_key, bucket_num)
        next_bucket_cache_key = "%s:%s:%s" % (zone_name, bucket_key, bucket_num)

        try:
            new_val = cache.incr(bucket_cache_key, 1)
        except ValueError:
            # bucket_cache_key not in the cache
            cache.add(bucket_cache_key, 1)
            new_val = 1

        return new_val
