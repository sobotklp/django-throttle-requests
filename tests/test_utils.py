# -*- coding: utf-8 -*-
from __future__ import with_statement # Python 2.5
from django.utils import unittest
from django.core.exceptions import ImproperlyConfigured

from throttle.utils import load_class_from_path

class test_load_module_from_path(unittest.TestCase):
    def test_invalid_modulename(self):
        with self.assertRaises(ImproperlyConfigured):
            load_class_from_path("allmodulenoklass")
        with self.assertRaises(ImproperlyConfigured):
            load_class_from_path("badmodule.badclass")
        with self.assertRaises(ImproperlyConfigured):
            load_class_from_path("tests.blah")
        with self.assertRaises(ImproperlyConfigured):
            load_class_from_path("tests.BADClass")

    def test_get_module(self):
        module = load_class_from_path("tests.backends.TestThrottleBackend")
        self.assertEqual(module.__name__, 'TestThrottleBackend')