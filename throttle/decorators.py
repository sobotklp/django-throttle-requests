import functools
from django.utils.decorators import available_attrs
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from exceptions import RateLimiterNotDefined

def throttle(view_func, bucket='default', *args):
    def _enfore_throttle(func):
        @functools.wraps(func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            throttles = getattr(func, '_throttles', [])
            setattr(func, 'throttles', throttles)
            return func(request, *args, **kwargs)
        return _wrapped_view

    # Validate the rate limiter used
    try:
        throttle_bucket = settings.THROTTLE_BUCKETS[bucket]
    except AttributeError:
        raise ImproperlyConfigured('@throttle is used, but settings.THROTTLE_BUCKETS is undefined')
    except KeyError:
        raise RateLimiterNotDefined(bucket)

    if view_func:
        _throttles = getattr(view_func, '_throttle_by', [])
        setattr(view_func, '_throttle_by', _throttles)
        return _enfore_throttle(view_func)
    return _enfore_throttle

