#!/usr/bin/env python
import os
import sys
import optparse

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'

def runtests(*tests, **kwargs):
    '''
    Invoke Django's test runner and collect output.
    Returns 0 if there were no failures
    '''
    from django.test.utils import get_runner
    from django.conf import settings

    if not tests:
        tests = ['tests']

    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=kwargs.get('verbosity', 1), interactive=kwargs.get('interactive', False), failfast=kwargs.get('failfast'))
    failures = test_runner.run_tests(tests)
    sys.exit(failures)

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('--failfast', action='store_true', default=False, dest='failfast')
    parser.add_option('--verbosity', type="int", default=1,dest='verbosity')
    (options, args) = parser.parse_args()

    runtests(failfast=options.failfast, varbosity=options.verbosity, *args)
