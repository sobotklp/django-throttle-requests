ROOT_URLCONF = ''
DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Need to use LocMemCache for testing 'throttle.backends.cache.CacheBackend'
# Can't use DummyCache because our functionality depends on the cache backend actually saving values.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',  # Bad for production!
    }
}

INSTALLED_APPS = [
    'throttle',
]

SECRET_KEY = "asdfnasdf;asdfasdfas"

TEST_RUNNER = 'django_nose.run_tests'
NOSE_ARGS = ['--with-xunit']

THROTTLE_ZONES = {
    'default': {
        'VARY': 'throttle.zones.RemoteIP',
        'NUM_BUCKETS': 2,  # Number of buckets worth of history to keep. Must be at least 2
        'BUCKET_CAPACITY': 5,  # Maximum number of requests allowed within BUCKET_INTERVAL
        'BUCKET_INTERVAL': 1  # Number of seconds to use each bucket.
    },
    'test2': {
        'VARY': 'throttle.zones.RemoteIP',
        'NUM_BUCKETS': 10,  # Number of buckets worth of history to keep. Must be at least 2
        'BUCKET_CAPACITY': 5,
        'BUCKET_INTERVAL': 60 * 15  # Number of seconds to use each bucket.
    }
}

THROTTLE_BACKEND = 'throttle.backends.redispy.RedisBackend'