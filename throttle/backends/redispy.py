from base import ThrottleBackendBase
try:
    import redis
except ImportError:
    from throttle.exceptions import ThrottleImproperlyConfigured
    raise ThrottleImproperlyConfigured("django-throttle-requests is configured to use redis, but redis-py is not installed!")

class RedisBackend(ThrottleBackendBase):
    def __init__(self):
        self.pool = redis.ConnectionPool(host='localhost', port=6379, db=0)

    def incr_bucket(self, zone_name, bucket_key, bucket_num, bucket_num_next, bucket_span, cost=1):
        conn = redis.Redis(connection_pool=self.pool)

        bucket_cache_key = "%s:%s" % (zone_name, bucket_key)

        # Execute operations inside a Redis transaction for atomicity
        pipe = conn.pipeline()
        pipe.hincrby(bucket_cache_key, bucket_num, cost)
        pipe.hdel(bucket_cache_key, bucket_num_next)
        pipe.expire(bucket_cache_key, time=bucket_span)

        try:
            new_value, expire_set, succeeded = pipe.execute()
            return new_value
        except redis.ConnectionError:
            return cost
