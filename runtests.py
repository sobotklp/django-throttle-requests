#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import optparse
from contextlib import contextmanager
from django.conf import settings

if not settings.configured:
    settings.configure(
        ROOT_URLCONF='',
        DEBUG=False,

        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },

        # Need to use LocMemCache for testing 'throttle.backends.cache.CacheBackend'
        # Can't use DummyCache because our functionality depends on the cache backend actually saving values.
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',  # Bad for production!
            }
        },

        INSTALLED_APPS=[
            'throttle',
        ],

        MIDDLEWARE_CLASSES=[],

        SECRET_KEY="asdfnasdf;asdfasdfas",

        THROTTLE_ZONES={
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

        THROTTLE_BACKEND='throttle.backends.cache.CacheBackend'
    )


@contextmanager
def record_coverage(enable_coverage=False):
    """
    Start the coverage module if we've chose to run with test coverage enabled.
    """

    # If coverage is not enabled, we don't have to bother with the rest of this function.
    if not enable_coverage:
        yield
        return

    try:
        from coverage import coverage
    except ImportError:
        print("You are attempting to run with coverage turned on, but the coverage module is not installed!", file=sys.stderr)
        print("Try sudo pip install coverage", file=sys.stderr)
        sys.exit(1)

    cov = coverage(include="throttle/*")
    cov.erase()
    cov.start()

    yield

    cov.stop()
    cov.html_report(directory='htmlcov')


def runtests(*test_args, **kwargs):
    """
    Invoke Django's test runner and collect output.
    Returns 0 if there were no failures
    """
    coverage_enabled = kwargs.get("coverage", False) or os.environ.get("WITH_COVERAGE", "False") == "True"

    import django
    from django.test.utils import get_runner

    with record_coverage(coverage_enabled):
        try:
            django.setup()
        except AttributeError:
            pass  # django.setup() only for Django >= 1.7

        if not test_args:
            test_args = ['throttle']
        TestRunner = get_runner(settings)
        test_runner = TestRunner(verbosity=kwargs.get('verbosity', 1), interactive=kwargs.get('interactive', False), failfast=kwargs.get('failfast'))
        failures = test_runner.run_tests(test_args)

    sys.exit(failures)


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('--failfast', action='store_true', default=False, dest='failfast')
    parser.add_option('--coverage', action='store_true', default=False, dest='coverage', help="generate an HTML coverage report")
    parser.add_option('--verbosity', type="int", default=1, dest='verbosity')
    (options, args) = parser.parse_args()

    runtests(failfast=options.failfast, verbosity=options.verbosity, coverage=options.coverage, *args)
