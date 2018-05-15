# -*- coding: utf-8 -*-
import hashlib

from throttle.backends.base import ThrottleBackendBase
try:
    import redis
    from redis.exceptions import NoScriptError
except ImportError:
    from throttle.exceptions import ThrottleImproperlyConfigured
    raise ThrottleImproperlyConfigured("django-throttle-requests is configured to use redis, but redis-py is not installed!")

# Lua script to update bucket data atomically.
# In general, lua scripts should be used instead of Redis transactions to ensure atomicity. Transactions may be
# deprecated at some point. Also, nutcracker does not support transactions but does support scripting
# as long as all keys used by the script hash to the same backend. The same limitation applies to Redis Cluster.
#
# Script takes 1 key and 4 arguments: <bucket_num>, <bucket_num_next>, <bucket_span>, <cost>
INCR_BUCKET_SCRIPT = """
local newval = redis.call('hincrby', KEYS[1], ARGV[1], ARGV[4])
redis.call('hdel', KEYS[1], ARGV[2])
redis.call('expire', KEYS[1], ARGV[3])
return newval
"""

INCR_BUCKET_SCRIPT_SHA1 = hashlib.sha1(INCR_BUCKET_SCRIPT.encode('utf-8')).hexdigest()

from django.conf import settings

class RedisBackend(ThrottleBackendBase):
    def __init__(self):
        
        THROTTLE_REDIS_HOST = getattr(settings, 'THROTTLE_REDIS_HOST', 'localhost')
        THROTTLE_REDIS_PORT = getattr(settings, 'THROTTLE_REDIS_PORT', 6379)
        THROTTLE_REDIS_DB = getattr(settings, 'THROTTLE_REDIS_DB', 0)
        THROTTLE_REDIS_AUTH = getattr(settings, 'THROTTLE_REDIS_AUTH', None)

        self.pool = redis.ConnectionPool(host=THROTTLE_REDIS_HOST, port=THROTTLE_REDIS_PORT, db=THROTTLE_REDIS_DB, password=THROTTLE_REDIS_AUTH)  #TODO: Parameterize connection parameters

    def incr_bucket(self, zone_name, bucket_key, bucket_num, bucket_num_next, bucket_span, cost=1):
        conn = redis.Redis(connection_pool=self.pool)

        bucket_cache_key = "%s:%s" % (zone_name, bucket_key)

        # Don't want to use redispy's `register_script` command here, because it uses SCRIPT LOAD, which isn't compatible
        # with nutcracker or Redis Cluster.
        try:
            try:
                return conn.evalsha(INCR_BUCKET_SCRIPT_SHA1, 1, bucket_cache_key, bucket_num, bucket_num_next, bucket_span, cost)
            except NoScriptError:
                return conn.eval(INCR_BUCKET_SCRIPT, 1, bucket_cache_key, bucket_num, bucket_num_next, bucket_span, cost)

        except redis.ConnectionError:
            return cost
