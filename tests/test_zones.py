from django.test import TestCase
from django.http import HttpResponse

from throttle.zones import RemoteIP, ThrottleZone


def _test_remote_ip(request):
    return HttpResponse(RemoteIP().process_view(request, _test_remote_ip, None, None))

try:
    from django.conf.urls import patterns, url
except ImportError: # django < 1.4
    from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^test/$', _test_remote_ip),
)

class TestRemoteIP(TestCase):
    urls = __module__

    def test_remoteIP(self):
        response = self.client.get('/test/')
        self.assertEqual(response.content, '127.0.0.1')

    def test_with_alternate_remote_addr(self):
        response = self.client.get('/test/', REMOTE_ADDR='10.5.2.1')
        self.assertEqual(response.content, '10.5.2.1')

    def test_with_proxied_ip(self):
        response = self.client.get('/test/', HTTP_X_FORWARDED_FOR='10.60.70.255', REMOTE_ADDR='10.5.2.1')
        self.assertEqual(response.content, '10.60.70.255')

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

        name, bucket_key, bucket_num, next_bucket_num, bucket_capacity = self.zone.process_view(self.fake_request, _test_remote_ip, (), {})

        self.assertEqual(name, 'testZone')
        self.assertEqual(bucket_key, '127.0.0.1') # because we're using RemoteIP
        self.assertEqual(bucket_num, 0)
        self.assertEqual(next_bucket_num, 1)
        self.assertEqual(bucket_capacity, 15)

        # Increment the timestamp - now it should fall into the second bucket
        self.zone.get_timestamp = lambda: 61
        name, bucket_key, bucket_num, next_bucket_num, bucket_capacity = self.zone.process_view(self.fake_request, _test_remote_ip, (), {})

        self.assertEqual(name, 'testZone')
        self.assertEqual(bucket_key, '127.0.0.1') # because we're using RemoteIP
        self.assertEqual(bucket_num, 1)
        self.assertEqual(next_bucket_num, 0)
        self.assertEqual(bucket_capacity, 15)

        # Increment the timestamp again - now should roll over to first bucket
        self.zone.get_timestamp = lambda: 121
        name, bucket_key, bucket_num, next_bucket_num, bucket_capacity = self.zone.process_view(self.fake_request, _test_remote_ip, (), {})

        self.assertEqual(name, 'testZone')
        self.assertEqual(bucket_key, '127.0.0.1') # because we're using RemoteIP
        self.assertEqual(bucket_num, 0)
        self.assertEqual(next_bucket_num, 1)
        self.assertEqual(bucket_capacity, 15)