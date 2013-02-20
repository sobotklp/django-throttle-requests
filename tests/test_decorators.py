# -*- coding: utf-8 -*-
from __future__ import with_statement # Python 2.5
from django.test import TestCase
from django.http import HttpResponse

from throttle.decorators import throttle
from throttle.exceptions import ThrottleZoneNotDefined

@throttle
def _test_view(request):
    return HttpResponse('OK')

@throttle
@throttle(zone='test2')
def _test_multiple_throttles(request):
    return HttpResponse("Photos")

def _test_view_not_throttled(request):
    return HttpResponse("Go ahead and DoS me!")

try:
    from django.conf.urls import patterns, url
except ImportError: # django < 1.4
    from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
                       url(r'^test/$', _test_view),
                       )

class test_throttle(TestCase):
    urls = __module__

    def test_view_marked(self):
        '''
        @throttle adds an attribute '_throttle_by' to views it decorates.
        The middleware uses that attribute to enforce limits
        '''
        self.assertFalse(hasattr(_test_view_not_throttled, '_throttle_zone'))
        self.assertTrue(hasattr(_test_view, '_throttle_zone'))
        self.assertEqual(_test_view._throttle_zone[0].vary.__class__.__name__, 'RemoteIP')

    def test_with_invalid_zone(self):
        '''
        @throttle throws an exception if an invalid zone is specified
        '''
        with self.assertRaises(ThrottleZoneNotDefined):
            _throttled_view = throttle(_test_view_not_throttled, zone='oœuf')

    def test_marked_view_returns(self):
        response = self.client.get('/test/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "OK")