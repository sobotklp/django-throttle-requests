import time
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from remoteip import RemoteIP

from throttle.exceptions import ThrottleZoneNotDefined, ThrottleImproperlyConfigured, RateLimitExceeded
from throttle.utils import load_class_from_path
from throttle.backends import get_backend

THROTTLE_ENABLED = getattr(settings, 'THROTTLE_ENABLED', not settings.DEBUG)

class ThrottleZone(object):
    def __init__(self, zone_name, vary_with, **config):
        self._zone_name = zone_name
        self.vary = vary_with(**config)
        self.config = config
        self.get_timestamp = lambda: int(time.time())

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

    def process_view(self, request, view_func, view_args, view_kwargs):
        # If THROTTLE_ENABLED is False, just return the response from the view.
        if not THROTTLE_ENABLED: #getattr(settings, 'THROTTLE_ENABLED', not settings.DEBUG):
            return view_func(request, *view_args, **view_kwargs)

        bucket_key = self.vary.get_bucket_key(request, view_func, view_args, view_kwargs)

        # Calculate the bucket offset to increment
        timestamp = self.get_timestamp()
        bucket_num = (timestamp % self.bucket_span) / self.bucket_interval
        bucket_num_next = (bucket_num+1) % self.num_buckets

        # Tell the backing store to increment the count
        new_value = get_backend().incr_bucket(self.name, bucket_key, bucket_num, bucket_num_next, self.bucket_span)

        # Has the bucket capacity been exceeded?
        if new_value > self.bucket_capacity:
            raise RateLimitExceeded(self.name)

        num_remaining = self.bucket_capacity - new_value

        # Execute the Django view. Add a few attributes to the response object.
        response = view_func(request, *view_args, **view_kwargs)
        response.throttle_limit = self.bucket_capacity
        response.throttle_remaining = num_remaining

        # Perform additional processing on the response object
        # TODO: Make this better
        response = self.process_response(request, response, remaining=num_remaining)

        return response

    def process_response(self, request, response, remaining=0):
        # TODO: Make this configurable
        response['X-Request-Limit-Limit'] = self.bucket_capacity
        response['X-Request-Limit-Remaining'] = remaining
        return response

    @property
    def name(self):
        return self._zone_name

def load_zone(zone_name, **config):
    vary_klass = load_class_from_path(config['VARY'])
    return ThrottleZone(zone_name, vary_klass, **config)

def get_zone(zone_name):
    try:
        throttle_zone = settings.THROTTLE_ZONES[zone_name]
        return load_zone(zone_name, **throttle_zone)
    except AttributeError:
        raise ImproperlyConfigured('@throttle is used, but settings.THROTTLE_ZONES is undefined')
    except KeyError:
        raise ThrottleZoneNotDefined(zone_name)
