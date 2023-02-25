# -*- coding: utf-8 -*-
from django.test import TestCase
from django.http import HttpResponse
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.urls import re_path
from django.test.utils import override_settings

from throttle.decorators import throttle
from throttle.exceptions import ThrottleZoneNotDefined


@throttle
def _test_view(request):
    return HttpResponse('OK')


@throttle
@throttle(zone='test2')
def _test_multiple_throttles(request):
    return HttpResponse("Photos")


@throttle(zone='test2')
def _test_view_with_parameters(request, id):
    return HttpResponse(str(id))


def _test_view_not_throttled(request):
    return HttpResponse("Go ahead and DoS me!")


class TestView(View):

    @method_decorator(throttle(zone='default'))
    def dispatch(self, *args, **kwargs):
        return super(TestView, self).dispatch(*args, **kwargs)

    def head(self, request, id):
        return HttpResponse("Metadata")

    def get(self, request, id):
        return HttpResponse(str(id))


# Explicitly create the view. This is only done for testing as we need to inspect the view code
test_generic_view = TestView.as_view()

urlpatterns = [
    re_path(r'^test/$', _test_view),
    re_path(r'^test/(\d+)/$', _test_view_with_parameters),
    re_path(r'^test-generic-view/(\d+)/?$', test_generic_view)
]


@override_settings(ROOT_URLCONF=__name__)
class test_throttle(TestCase):

    def test_view_marked(self):
        '''
        @throttle adds an attribute 'throttle_zone' to views it decorates.
        '''
        self.assertFalse(hasattr(_test_view_not_throttled, 'throttle_zone'))
        self.assertTrue(hasattr(_test_view, 'throttle_zone'))
        self.assertEqual(_test_view.throttle_zone.vary.__class__.__name__, 'RemoteIP')

    def test_with_invalid_zone(self):
        '''
        @throttle throws an exception if an invalid zone is specified
        '''
        with self.assertRaises(ThrottleZoneNotDefined):
            _throttled_view = throttle(_test_view_not_throttled, zone='oœuf')
            _throttled_view(object)

    def test_marked_view_returns(self):
        response = self.client.get('/test/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "OK")

    def test_marked_view_with_params(self):
        response = self.client.get('/test/99/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "99")

    def test_returns_403_if_exceeded(self):

        # THROTTLE_ZONE 'default' allows 5 requests/second
        for i in range(5):
            response = self.client.get('/test/', REMOTE_ADDR='test_returns_403_if_exceeded')
            self.assertEqual(response.status_code, 200, '%ith iteration' % i)

        # Now the next request should fail
        response = self.client.get('/test/', REMOTE_ADDR='test_returns_403_if_exceeded')
        self.assertEqual(response.status_code, 403)

    def test_marked_class_view_returns(self):
        response = self.client.get('/test-generic-view/100')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "100")

    def test_marked_class_view_returns_403_if_exceeded(self):
        # THROTTLE_ZONE 'default' allows 5 requests/second
        for i in range(5):
            response = self.client.get('/test-generic-view/%i' % i, REMOTE_ADDR='test_marked_class_view_returns_403_if_exceeded')
            self.assertEqual(response.status_code, 200)

        # Now the next request should fail
        response = self.client.get('/test-generic-view/%i' % i, REMOTE_ADDR='test_marked_class_view_returns_403_if_exceeded')
        self.assertEqual(response.status_code, 403)
