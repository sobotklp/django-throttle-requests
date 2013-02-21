import functools
from django.utils.decorators import available_attrs

from zones import get_zone

def throttle(view_func=None, zone='default'):
    def _enforce_throttle(func):
        @functools.wraps(func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            # Get zone from cache
            _throttle_zone = get_zone(zone)

            # raises an exception if the rate limit is exceeded
            response = _throttle_zone.process_view(request, func, args, kwargs)
            return response
        return _wrapped_view

    # Validate the rate limiter bucket
    _zone = get_zone(zone)

    if view_func:
        setattr(view_func, '_throttle_zone', _zone)
        return _enforce_throttle(view_func)
    return _enforce_throttle

