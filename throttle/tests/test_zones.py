from __future__ import with_statement  # Python 2.5
from django.test import TestCase
from django.http import HttpResponse
from django.conf.urls import patterns, url

from throttle.zones import RemoteIP, ThrottleZone


def _test_remote_ip(request):
    return HttpResponse(RemoteIP().get_bucket_key(request, _test_remote_ip, None, None))


urlpatterns = patterns('',
    url(r'^test/$', _test_remote_ip),
)

class TestRemoteIP(TestCase):
    urls = __module__

    def test_remoteIP(self):
        response = self.client.get('/test/')
        self.assertContains(response, '127.0.0.1')

    def test_with_alternate_remote_addr(self):
        response = self.client.get('/test/', REMOTE_ADDR='10.5.2.1')
        self.assertContains(response, '10.5.2.1')

    def test_with_proxied_ip(self):
        response = self.client.get('/test/', HTTP_X_FORWARDED_FOR='10.60.70.255', REMOTE_ADDR='10.5.2.1')
        self.assertContains(response, '10.60.70.255')

class Test_ThrottleZone(TestCase):
    # TODO: Add more tests for the constructor
    def setUp(self):
        self.zone = ThrottleZone('testZone', RemoteIP, BUCKET_INTERVAL=60, NUM_BUCKETS=2, BUCKET_CAPACITY=15)

        class FakeRequest:
            META = {
                'REMOTE_ADDR': '127.0.0.1',
            }

        self.fake_request = FakeRequest()

    def test_process_view(self):
        # Don't want unit tests to rely on the value of time.time()
        self.zone.get_timestamp = lambda: 1

        response = self.zone.process_view(self.fake_request, _test_remote_ip, (), {})
        self.assertEqual(response.throttle_remaining, 14)

        response = self.zone.process_view(self.fake_request, _test_remote_ip, (), {})
        self.assertEqual(response.throttle_remaining, 13)

        # Increment the timestamp - now it should fall into the second bucket
        self.zone.get_timestamp = lambda: 61
        response = self.zone.process_view(self.fake_request, _test_remote_ip, (), {})
        self.assertEqual(response.throttle_remaining, 14)

        # Increment the timestamp again - now should roll over to first bucket
        self.zone.get_timestamp = lambda: 121
        response = self.zone.process_view(self.fake_request, _test_remote_ip, (), {})
        self.assertEqual(response.throttle_remaining, 14)

    def test_obeys_THROTTLE_ENABLED_setting(self):
        # Don't want unit tests to rely on the value of time.time()
        self.zone.get_timestamp = lambda: 1

        import throttle.zones
        old_THROTTLE_ENABLED = throttle.zones.THROTTLE_ENABLED
        throttle.zones.THROTTLE_ENABLED = False

        # Should be able to make more than 15 calls now
        for i in range(20):
            response = self.zone.process_view(self.fake_request, _test_remote_ip, (), {})
            self.assertEqual(response.status_code, 200)
            self.assertFalse(hasattr(response, 'throttle_remaining'))

        throttle.zones.THROTTLE_ENABLED = old_THROTTLE_ENABLED
