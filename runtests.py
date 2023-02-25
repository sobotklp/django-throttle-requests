#!/usr/bin/env python
import os
import sys
import argparse
from contextlib import contextmanager
from django.conf import settings


def _apply_settings(use_redis):
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
                'ALGORITHM': 'fixed-bucket',  # default
                'BUCKET_CAPACITY': 5,  # Maximum number of requests allowed within BUCKET_INTERVAL
                'BUCKET_INTERVAL': 1,  # Number of seconds to use each bucket.
            },
            'test2': {
                'VARY': 'throttle.zones.RemoteIP',
                'ALGORITHM': 'fixed-bucket',  # default
                'BUCKET_CAPACITY': 5,  # Maximum number of requests allowed within BUCKET_INTERVAL
                'BUCKET_INTERVAL': 60,  # Number of seconds to use each bucket.
            },
            'gcra_test': {
                'VARY': 'throttle.zones.RemoteIP',
                'ALGORITHM': 'gcra',
                'BUCKET_CAPACITY': 10,  # Maximum number of requests allowed within window BUCKET_INTERVAL
                'BUCKET_INTERVAL': 10,  # Length of window
            },
        },

        THROTTLE_BACKEND=('throttle.backends.redispy.RedisBackend' if use_redis else 'throttle.backends.cache.CacheBackend')
    )


@contextmanager
def record_coverage(enable_coverage=False):
    """
    Start the coverage module if we chose to run with test coverage enabled.
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
    use_redis = kwargs.get('use_redis', False)
    _apply_settings(use_redis)

    import django
    from django.test.utils import get_runner

    with record_coverage(coverage_enabled):
        django.setup()

        if not test_args:
            test_args = ['throttle']
        TestRunner = get_runner(settings)
        test_runner = TestRunner(verbosity=kwargs.get('verbosity', 1), interactive=kwargs.get('interactive', False), failfast=kwargs.get('failfast'))
        failures = test_runner.run_tests(test_args)

    sys.exit(failures)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run unit tests for django-throttle-requests")
    parser.add_argument('--failfast', action='store_true', default=False, dest='failfast')
    parser.add_argument('--coverage', action='store_true', default=False, dest='coverage', help="generate an HTML coverage report")
    parser.add_argument('--use-redis', action='store_true', default=False, dest='use_redis',
                      help="Use local Redis server as backing store")
    parser.add_argument('--verbosity', type=int, default=1, dest='verbosity')
    args = parser.parse_args()

    runtests(failfast=args.failfast, verbosity=args.verbosity, coverage=args.coverage, use_redis=args.use_redis)
