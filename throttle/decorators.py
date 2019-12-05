import functools

from throttle.zones import get_zone


def throttle(view_func=None, zone='default'):
    def decorator(func):

        @functools.wraps(func, assigned=functools.WRAPPER_ASSIGNMENTS)
        def _wrapped_view(request, *args, **kwargs):
            # Get zone from cache
            _throttle_zone = get_zone(zone)

            # raises an exception if the rate limit is exceeded
            response = _throttle_zone.process_view(request, func, args, kwargs)
            return response

        # Validate the rate limiter bucket
        _zone = get_zone(zone)

        if func:
            setattr(_wrapped_view, 'throttle_zone', _zone)
            return _wrapped_view
        return _wrapped_view

    # Validate the rate limiter bucket
    _zone = get_zone(zone)
    if view_func:
        setattr(view_func, 'throttle_zone', _zone)
        return decorator(view_func)
    return decorator
