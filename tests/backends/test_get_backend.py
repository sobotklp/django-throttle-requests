# -*- coding: utf-8 -*-
from __future__ import with_statement # Python 2.5
from django.utils import unittest
from django.core.exceptions import ImproperlyConfigured

from throttle.backends import get_backend

class test_get_backend(unittest.TestCase):
    def test_get_backend_invalid_modulename(self):
        with self.assertRaises(ImproperlyConfigured):
            get_backend("tests.backends.BADThrottleBackend")

    def test_get_backend(self):
        backend = get_backend("tests.backends.TestThrottleBackend")
        self.assertEqual(backend.__class__.__name__, 'TestThrottleBackend')