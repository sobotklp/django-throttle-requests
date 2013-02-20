import os
import django

TEST_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)))

ROOT_URLCONF='',
DEBUG=False,
SITE_ID=1,

if django.VERSION[:2] >= (1, 3):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
            }
    }
else:
    DATABASE_ENGINE = 'sqlite3'

INSTALLED_APPS = [
    'throttle',
    'tests',
    ]

TEMPLATE_DIRS = (
    # Specifically choose a name that will not be considered
    # by app_directories loader, to make sure each test uses
    # a specific template without considering the others.
    os.path.join(TEST_DIR, 'test_templates'),
)

SECRET_KEY = "asdfnasdf;asdfasdfas"

TEST_RUNNER = 'django_nose.run_tests'
NOSE_ARGS= ['--with-xunit']

THROTTLE_BUCKETS = {
    'default': {
        'VARY': 'throttle.strategies.RemoteIP',
        'NUM_BUCKETS': 10, # Number of buckets worth of history to keep. Must be at least 2
        'BUCKET_CAPACITY': 5,
        'BUCKET_TIME': 60*15 # Number of seconds to use each bucket.
    }
}

THROTTLE_BACKEND = 'throttle.backends.cache.CacheBackend'