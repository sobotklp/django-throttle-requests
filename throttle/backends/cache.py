import time
from django.core.cache import cache
from throttle.backends.base import ThrottleBackendBase


class CacheBackend(ThrottleBackendBase):
    def __init__(self):
        self.cache = cache
        self.time_function = lambda: time.time()

    def incr_bucket(self, zone_name, bucket_key, bucket_span, limit, cost=1):
        bucket_cache_key = "%s:%s" % (zone_name, bucket_key)

        # Increment the value of the current bucket.
        # Note that the Django documentation states that this operation is not guaranteed
        # to be atomic.
        try:
            new_val = self.cache.incr(bucket_cache_key, cost)
        except ValueError:
            # bucket_cache_key not in the cache
            self.cache.add(bucket_cache_key, cost, bucket_span)
            new_val = cost

        return new_val

    def gcra(self, zone_name, bucket_key, bucket_span, limit):
        """
        Implement Generic Cell Rate Algorithm using Django's cache backend

        Don't use this in production, since this function is not atomic and there's
        currently no locking facility. This produces a race condition that lowers the
        reliability of the request limiter if used on multiple application processes.

        For production, please use the redispy implementation.
        """
        bucket_cache_key = "%s:%s" % (zone_name, bucket_key)

        now = self.time_function()
        between_reqs = bucket_span / limit
        try:
            prior_value = float(self.cache.get_or_set(bucket_cache_key, 0, bucket_span))
        except ValueError:
            prior_value = 0

        tat = max(prior_value, now)
        if tat - now <= bucket_span - between_reqs:
            new_tat = max(now, tat) + between_reqs
            self.cache.set(bucket_cache_key, new_tat, bucket_span)
            return round(((new_tat - now) / between_reqs))  # How many more requests are allowed

        return limit + 1  # Limit exceeded

    ALGORITHMS = {
        'fixed-bucket': incr_bucket,
        'gcra': gcra,
    }

    def get_algorithm(self, algorithm_name):
        return self.ALGORITHMS[algorithm_name]
