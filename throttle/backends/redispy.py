# -*- coding: utf-8 -*-
import hashlib
from django.conf import settings

from throttle.backends.base import ThrottleBackendBase
try:
    import redis
    from redis.exceptions import NoScriptError
except ImportError:
    from throttle.exceptions import ThrottleImproperlyConfigured
    raise ThrottleImproperlyConfigured("django-throttle-requests is configured to use redis, but redis-py is not installed!")

# Lua script to update bucket data atomically.
# In general, lua scripts should be used instead of Redis transactions to ensure atomicity. Transactions may be
# deprecated at some point.
#
# Script takes 1 key and 2 arguments: <bucket_interval>, <cost>
INCR_BUCKET_SCRIPT = """
local newval = redis.call('INCRBY', KEYS[1], ARGV[2])
redis.call('EXPIRE', KEYS[1], ARGV[1])
return newval
"""

INCR_BUCKET_SCRIPT_SHA1 = hashlib.sha1(INCR_BUCKET_SCRIPT.encode('utf-8')).hexdigest()


# Since this script is non-deterministic (it uses the Redis TIME command),
# ensure that your Redis server is configured with "script effects replication."
# This is the default setting for Redis 5.0.0+
#
# Script takes 1 key and 2 arguments: <bucket_interval>, <limit>
GCRA_SCRIPT = """
local bucket_interval = ARGV[1]
local limit = ARGV[2]
local time = redis.call('TIME')
local now = time[1] + (time[2] / 1000000)
local between_reqs = bucket_interval / limit
redis.call('SET', KEYS[1], 0, 'NX', 'EX', bucket_interval)
local tat = math.max(redis.call('GET', KEYS[1]), now)
if tat - now <= bucket_interval - between_reqs then
    local new_tat = math.max(now, tat) + between_reqs
    redis.call('SET', KEYS[1], tostring(new_tat), 'EX', bucket_interval)
    return ((new_tat - now) / between_reqs) -- request is allowed
end

return limit + 1 -- request is blocked
"""

GCRA_SCRIPT_SHA1 = hashlib.sha1(GCRA_SCRIPT.encode('utf-8')).hexdigest()


class RedisBackend(ThrottleBackendBase):

    def __init__(self):

        THROTTLE_REDIS_HOST = getattr(settings, 'THROTTLE_REDIS_HOST', 'localhost')
        THROTTLE_REDIS_PORT = getattr(settings, 'THROTTLE_REDIS_PORT', 6379)
        THROTTLE_REDIS_DB = getattr(settings, 'THROTTLE_REDIS_DB', 0)
        THROTTLE_REDIS_AUTH = getattr(settings, 'THROTTLE_REDIS_AUTH', None)

        self.pool = redis.ConnectionPool(host=THROTTLE_REDIS_HOST, port=THROTTLE_REDIS_PORT, db=THROTTLE_REDIS_DB, password=THROTTLE_REDIS_AUTH)

    def incr_bucket(self, zone_name, bucket_key, bucket_interval, limit, cost=1):
        """
        Fixed window bucket algorithm using Redis scripting
        """
        conn = redis.Redis(connection_pool=self.pool)

        bucket_cache_key = "%s:%s" % (zone_name, bucket_key)

        try:
            try:
                return conn.evalsha(INCR_BUCKET_SCRIPT_SHA1, 1, bucket_cache_key, bucket_interval, cost)
            except NoScriptError:
                return conn.eval(INCR_BUCKET_SCRIPT, 1, bucket_cache_key, bucket_interval, cost)

        except redis.ConnectionError:
            return cost

    def gcra(self, zone_name, bucket_key, bucket_interval, limit):
        """
        Generic Cell Rate Algorithm using Redis scripting
        """
        conn = redis.Redis(connection_pool=self.pool)

        bucket_cache_key = "%s:%s" % (zone_name, bucket_key)

        try:
            try:
                return conn.evalsha(GCRA_SCRIPT_SHA1, 1, bucket_cache_key, bucket_interval, limit)
            except NoScriptError:
                return conn.eval(GCRA_SCRIPT, 1, bucket_cache_key, bucket_interval, limit)

        except redis.ConnectionError:
            return 1

    ALGORITHMS = {
        'fixed-bucket': incr_bucket,
        'gcra': gcra,
    }

    def get_algorithm(self, algorithm_name):
        return self.ALGORITHMS[algorithm_name]
