#!/usr/bin/env python
import os
import sys
import optparse
from django.conf import settings

if not settings.configured:
    settings.configure(
        ROOT_URLCONF = '',
        DEBUG = False,

        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
                }
        },

        # Need to use LocMemCache for testing 'throttle.backends.cache.CacheBackend'
        # Can't use DummyCache because our functionality depends on the cache backend actually saving values.
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',  # Bad for production!
            }
        },

        INSTALLED_APPS = [
            'throttle',
            ],

        SECRET_KEY = "asdfnasdf;asdfasdfas",

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
        },

        THROTTLE_BACKEND = 'throttle.backends.cache.CacheBackend'
        )

def runtests(*test_args, **kwargs):
    '''
    Invoke Django's test runner and collect output.
    Returns 0 if there were no failures
    '''
    from django.test.utils import get_runner

    if not test_args:
        test_args = ['throttle']
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=kwargs.get('verbosity', 1), interactive=kwargs.get('interactive', False), failfast=kwargs.get('failfast'))
    failures = test_runner.run_tests(test_args)
    sys.exit(failures)

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('--failfast', action='store_true', default=False, dest='failfast')
    parser.add_option('--verbosity', type="int", default=1,dest='verbosity')
    (options, args) = parser.parse_args()

    runtests(failfast=options.failfast, varbosity=options.verbosity, *args)
