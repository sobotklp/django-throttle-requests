# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.utils import override_settings
from django.http import HttpResponse

from throttle.decorators import throttle
from throttle.exceptions import RateLimiterNotDefined

@throttle
def _test_view(request):
    return HttpResponse('OK')

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
        self.assertFalse(hasattr(_test_view_not_throttled, '_throttle_by'))
        self.assertTrue(hasattr(_test_view, '_throttle_by'))

    def test_with_invalid_bucket(self):
        '''
        @throttle throws an exception if an invalid bucket is specified
        '''
        with self.assertRaises(RateLimiterNotDefined):
            _throttled_view = throttle(_test_view_not_throttled, bucket='oœuf')

    def test_marked_view_returns(self):
        response = self.client.get('/test/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "OK")