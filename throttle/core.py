from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from backends import get_backend
from exceptions import RateLimitExceeded

if getattr(settings, 'THROTTLE_BACKEND', ''):
    backend = get_backend(settings.THROTTLE_BACKEND)
else:
    raise ImproperlyConfigured('@throttle was used, but settings.THROTTLE_BACKEND is not set')

def throttle_request(view_func, request, zones, *args, **kwargs):
    for zone in zones:
        bucket_key = zone.process_view(request, view_func, args, kwargs)
        #raise RateLimitExceeded(bucket)
        pass