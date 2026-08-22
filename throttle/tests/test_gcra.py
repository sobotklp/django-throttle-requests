from typing import ClassVar

from django.http import HttpResponse
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import re_path

from throttle.exceptions import RateLimitExceeded
from throttle.zones import RemoteIP, ThrottleZone


def _test_remote_ip(request):
    return HttpResponse(RemoteIP().get_bucket_key(request, _test_remote_ip, None, None))


urlpatterns = [
    re_path(r'^test/$', _test_remote_ip),
]


@override_settings(ROOT_URLCONF=__name__)
class Test_GCRAAlgorithm(TestCase):

    def setUp(self):
        self.zone = ThrottleZone('gcra_test', RemoteIP, BUCKET_INTERVAL=10, BUCKET_CAPACITY=10, ALGORITHM='gcra')

        class FakeRequest:
            META: ClassVar[dict[str, str]] = {
                'REMOTE_ADDR': '127.0.0.1',
            }

        self.fake_request = FakeRequest()

    def test_gcra(self):
        # First request should succeed
        response = self.zone.process_view(self.fake_request, _test_remote_ip, (), {})
        self.assertEqual(response.throttle_remaining, 9)

        # Next nine requests should succeed
        for i in range(9):
            response = self.zone.process_view(self.fake_request, _test_remote_ip, (), {})

        # Eleventh one should fail
        with self.assertRaises(RateLimitExceeded):
            response = self.zone.process_view(self.fake_request, _test_remote_ip, (), {})
