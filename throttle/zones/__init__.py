from django.core.exceptions import ImproperlyConfigured
from remoteip import RemoteIP

from throttle.exceptions import ThrottleZoneNotDefined
from throttle.utils import load_class_from_path

def load_zone(**config):
    klass = load_class_from_path(config['VARY'])
    return klass(**config)

def get_zone(zone_name):
    from django.conf import settings

    try:
        throttle_zone = settings.THROTTLE_ZONES[zone_name]
        return load_zone(**throttle_zone)
    except AttributeError:
        raise ImproperlyConfigured('@throttle is used, but settings.THROTTLE_ZONES is undefined')
    except KeyError:
        raise ThrottleZoneNotDefined(zone_name)
