from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from backends import get_backend
from exceptions import RateLimitExceeded

if getattr(settings, 'THROTTLE_BACKEND', ''):
    backend = get_backend(settings.THROTTLE_BACKEND)
else:
    raise ImproperlyConfigured('@throttle was used, but settings.THROTTLE_BACKEND is not set')

def throttle_request(view_func, request, buckets, *args, **kwargs):
    print view_func.__name__
    for bucket in buckets:
        #raise RateLimitExceeded(bucket)
        pass