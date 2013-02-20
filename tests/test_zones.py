from django.test import TestCase
from django.http import HttpResponse

from throttle.zones import RemoteIP

def _test_view(request):
    return HttpResponse(RemoteIP().process_view(request, _test_view, None, None))

try:
    from django.conf.urls import patterns, url
except ImportError: # django < 1.4
    from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^test/$', _test_view),
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
        response = self.client.get('/test/', HTTP_X_FORWARDED_FOR='10.60.70.255')
        self.assertEqual(response.content, '10.60.70.255')