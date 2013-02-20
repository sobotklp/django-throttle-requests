import time
from django.core.exceptions import ImproperlyConfigured
from remoteip import RemoteIP

from throttle.exceptions import ThrottleZoneNotDefined, ThrottleImproperlyConfigured
from throttle.utils import load_class_from_path

class ThrottleZone(object):
    def __init__(self, zone_name, vary_with, **config):
        self._zone_name = zone_name
        self.vary = vary_with(**config)

        try:
            self.bucket_interval = int(config['BUCKET_INTERVAL'])
        except KeyError:
            raise ThrottleImproperlyConfigured('A THROTTLE_ZONE entry missing BUCKET_INTERVAL parameter)')
        try:
            self.num_buckets = int(config['NUM_BUCKETS'])
        except KeyError:
            raise ThrottleImproperlyConfigured('THROTTLE_ZONE \'%s\' entry missing NUM_BUCKETS parameter)' % (zone_name))
        try:
            self.bucket_capacity = int(config['BUCKET_CAPACITY'])
        except KeyError:
            raise ThrottleImproperlyConfigured('THROTTLE_ZONE \'%s\' entry missing BUCKET_CAPACITY parameter)' % (zone_name))

        self.bucket_span = self.bucket_interval * self.num_buckets
        self.config = config

        self.get_timestamp = lambda: int(time.time())

    def process_view(self, request, view_func, view_args, view_kwargs):
        bucket_key = self.vary.process_view(request, view_func, view_args, view_kwargs)

        # Calculate the bucket offset to increment
        timestamp = self.get_timestamp()
        bucket_num = (timestamp % self.bucket_span) / self.bucket_interval
        bucket_num_next = (bucket_num+1) % self.num_buckets

        return (self.name, bucket_key, bucket_num, bucket_num_next, self.bucket_capacity)

    @property
    def name(self):
        return self._zone_name

def load_zone(zone_name, **config):
    vary_klass = load_class_from_path(config['VARY'])
    return ThrottleZone(zone_name, vary_klass, **config)

def get_zone(zone_name):
    from django.conf import settings

    try:
        throttle_zone = settings.THROTTLE_ZONES[zone_name]
        return load_zone(zone_name, **throttle_zone)
    except AttributeError:
        raise ImproperlyConfigured('@throttle is used, but settings.THROTTLE_ZONES is undefined')
    except KeyError:
        raise ThrottleZoneNotDefined(zone_name)
