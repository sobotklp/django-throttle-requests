from django.test import TestCase
from django.http import HttpResponse
from django.urls import re_path
from django.test.utils import override_settings

from throttle.zones import RemoteIP, ThrottleZone
from throttle.exceptions import ThrottleImproperlyConfigured


def _test_remote_ip(request):
    return HttpResponse(RemoteIP().get_bucket_key(request, _test_remote_ip, None, None))


urlpatterns = [
    re_path(r'^test/$', _test_remote_ip),
]


@override_settings(ROOT_URLCONF=__name__)
class TestRemoteIP(TestCase):

    def test_remoteIP(self):
        response = self.client.get('/test/')
        self.assertContains(response, '127.0.0.1')

    def test_with_alternate_remote_addr(self):
        response = self.client.get('/test/', REMOTE_ADDR='10.5.2.1')
        self.assertContains(response, '10.5.2.1')

    def test_with_proxied_ip(self):
        response = self.client.get('/test/', HTTP_X_FORWARDED_FOR='10.60.70.255', REMOTE_ADDR='10.5.2.1')
        self.assertContains(response, '10.60.70.255')


@override_settings(ROOT_URLCONF=__name__)
class Test_ThrottleZone(TestCase):
    # TODO: Add more tests for the constructor
    def setUp(self):
        self.zone = ThrottleZone('testZone', RemoteIP, BUCKET_INTERVAL=60, BUCKET_CAPACITY=15)

        class FakeRequest:
            META = {
                'REMOTE_ADDR': '127.0.0.1',
            }

        self.fake_request = FakeRequest()

    def test_unsupported_algorithm(self):
        with self.assertRaises(ThrottleImproperlyConfigured):
            ThrottleZone('testZone', RemoteIP, BUCKET_INTERVAL=60, BUCKET_CAPACITY=15, ALGORITHM="FAKE")

    def test_process_view(self):
        response = self.zone.process_view(self.fake_request, _test_remote_ip, (), {})
        self.assertEqual(response.throttle_remaining, 14)

        response = self.zone.process_view(self.fake_request, _test_remote_ip, (), {})
        self.assertEqual(response.throttle_remaining, 13)

    def test_obeys_THROTTLE_ENABLED_setting(self):
        import throttle.zones
        old_THROTTLE_ENABLED = throttle.zones.THROTTLE_ENABLED
        throttle.zones.THROTTLE_ENABLED = False

        # Should be able to make more than 15 calls now
        for i in range(20):
            response = self.zone.process_view(self.fake_request, _test_remote_ip, (), {})
            self.assertEqual(response.status_code, 200)
            self.assertFalse(hasattr(response, 'throttle_remaining'))

        throttle.zones.THROTTLE_ENABLED = old_THROTTLE_ENABLED
