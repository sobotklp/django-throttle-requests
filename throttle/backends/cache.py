from base import ThrottleBackendBase
from django.core.cache import cache

class CacheBackend(ThrottleBackendBase):
    def __init__(self):
        self.cache = cache

    def incr_bucket(self, zone_name, bucket_key, bucket_num, bucket_num_next):
        bucket_cache_key = "%s:%s:%s" % (zone_name, bucket_key, bucket_num)
        next_bucket_cache_key = "%s:%s:%s" % (zone_name, bucket_key, bucket_num_next)

        # Increment the value of the current bucket
        try:
            new_val = self.cache.incr(bucket_cache_key, 1)
        except ValueError:
            # bucket_cache_key not in the cache
            self.cache.add(bucket_cache_key, 1)
            new_val = 1

        # Reset the value of the next bucket
        self.cache.set(next_bucket_cache_key, 0)

        return new_val
