# -*- coding: utf-8 -*-
from __future__ import with_statement # Python 2.5
try:
    from django.utils import unittest
except ImportError:  # Not available in Django 1.9
    import unittest

from django.core.exceptions import ImproperlyConfigured

from throttle.backends import load_backend_from_path

class test_get_backend(unittest.TestCase):
    def test_load_backend_from_path_invalid_modulename(self):
        with self.assertRaises(ImproperlyConfigured):
            load_backend_from_path("throttle.tests.backends.BADThrottleBackend")

    def test_load_backend_from_path(self):
        backend = load_backend_from_path("throttle.tests.backends.TestThrottleBackend")
        self.assertEqual(backend.__class__.__name__, 'TestThrottleBackend')
