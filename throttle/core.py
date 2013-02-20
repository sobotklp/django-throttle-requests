from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from backends import get_backend
from exceptions import RateLimitExceeded

if getattr(settings, 'THROTTLE_BACKEND', ''):
    backend = get_backend(settings.THROTTLE_BACKEND)
else:
    raise ImproperlyConfigured('@throttle was used, but settings.THROTTLE_BACKEND is not set')

def throttle_request(view_func, request, zones, *view_args, **view_kwargs):
    for zone in zones:
        zone_name, bucket_key, bucket_num = zone.process_view(request, view_func, view_args, view_kwargs)

        print zone_name, bucket_key, bucket_num

        value = backend.test_limit(zone_name, bucket_key, bucket_num)
        print value

        pass