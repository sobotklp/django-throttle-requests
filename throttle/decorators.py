import functools
from django.utils.decorators import available_attrs

from core import throttle_request
from zones import get_zone

def throttle(view_func=None, zone='default'):
    def _enforce_throttle(func):
        @functools.wraps(func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            _buckets = getattr(view_func, '_throttle_by', [])

            # raises an exception if the rate limit is exceeded
            throttle_request(func, request, _buckets, *args, **kwargs)

            # rate limit not exceeded - call view
            response = func(request, *args, **kwargs)
            return response
        return _wrapped_view

    # Validate the rate limiter bucket
    _zone = get_zone(zone)

    if view_func:
        _throttles = getattr(view_func, '_throttle_by', [])
        _throttles.append(_zone)
        setattr(view_func, '_throttle_by', _throttles)
        return _enforce_throttle(view_func)
    return _enforce_throttle

