from django.core.exceptions import ImproperlyConfigured
from remoteip import RemoteIP

from throttle.exceptions import ThrottleZoneNotDefined
from throttle.utils import load_class_from_path

class ThrottleZone(object):
    def __init__(self, vary_with, **config):
        self.vary = vary_with(**config)
        self.config = config

    def process_view(self, request, view_func, view_args, view_kwargs):
        bucket_key = self.vary.process_view(request, view_func, view_args, view_kwargs)


def load_zone(**config):
    vary_klass = load_class_from_path(config['VARY'])
    return ThrottleZone(vary_klass, **config)

def get_zone(zone_name):
    from django.conf import settings

    try:
        throttle_zone = settings.THROTTLE_ZONES[zone_name]
        return load_zone(**throttle_zone)
    except AttributeError:
        raise ImproperlyConfigured('@throttle is used, but settings.THROTTLE_ZONES is undefined')
    except KeyError:
        raise ThrottleZoneNotDefined(zone_name)
