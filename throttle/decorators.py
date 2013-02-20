import functools
from django.utils.decorators import available_attrs
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from exceptions import RateLimiterNotDefined
from core import throttle_request

def throttle(view_func=None, bucket='default'):
    def _enforce_throttle(func):
        @functools.wraps(func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            _buckets = getattr(view_func, '_throttle_by', [])

            # raises an exception if the rate limit is exceeded
            throttle_request(func, request, _buckets)

            # rate limit not exceeded - call view
            response = func(request, *args, **kwargs)
            return response
        return _wrapped_view

    # Validate the rate limiter bucket
    try:
        throttle_bucket = settings.THROTTLE_TYPES[bucket]
    except AttributeError:
        raise ImproperlyConfigured('@throttle is used, but settings.THROTTLE_TYPES is undefined')
    except KeyError:
        raise RateLimiterNotDefined(bucket)

    if view_func:
        _throttles = getattr(view_func, '_throttle_by', [])
        _throttles.append(bucket)
        setattr(view_func, '_throttle_by', _throttles)
        return _enforce_throttle(view_func)
    return _enforce_throttle

