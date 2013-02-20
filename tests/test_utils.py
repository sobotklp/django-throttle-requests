# -*- coding: utf-8 -*-
from __future__ import with_statement # Python 2.5
from django.utils import unittest
from django.core.exceptions import ImproperlyConfigured

from throttle.backends import get_backend

class test_load_module_from_path(unittest.TestCase):
    def test_invalid_modulename(self):
        with self.assertRaises(ImproperlyConfigured):
            get_backend("allmodulenoklass")
        with self.assertRaises(ImproperlyConfigured):
            get_backend("badmodule.badclass")
        with self.assertRaises(ImproperlyConfigured):
            get_backend("tests.blah")
        with self.assertRaises(ImproperlyConfigured):
            get_backend("tests.BADClass")

    def test_get_module(self):
        module = get_backend("tests.backends.TestThrottleBackend")
        self.assertEqual(module.__class__.__name__, 'TestThrottleBackend')