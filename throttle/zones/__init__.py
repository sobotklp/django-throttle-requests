import time
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from throttle.zones.remoteip import RemoteIP
from throttle.exceptions import ThrottleZoneNotDefined, ThrottleImproperlyConfigured, RateLimitExceeded
from throttle.utils import load_class_from_path, serialize_bucket_key
from throttle.backends import get_backend

THROTTLE_ENABLED = getattr(settings, 'THROTTLE_ENABLED', not settings.DEBUG)

_THROTTLE_ZONES = {}


class ThrottleZone(object):
    def __init__(self, zone_name, vary_with, **config):
        self._zone_name = zone_name
        self.vary = vary_with(**config)
        self.config = config
        self.get_timestamp = lambda: int(time.time())

        try:
            self.bucket_interval = int(config['BUCKET_INTERVAL'])
            if self.bucket_interval <= 0:
                raise ValueError
        except KeyError:
            raise ThrottleImproperlyConfigured('THROTTLE_ZONE[\'%s\'] missing BUCKET_INTERVAL parameter)' % zone_name)
        except ValueError:
            raise ThrottleImproperlyConfigured('THROTTLE_ZONE[\'%s\'][\'BUCKET_INTERVAL\'] must be > 0' % zone_name)

        try:
            self.num_buckets = int(config['NUM_BUCKETS'])
            if self.num_buckets < 2:
                raise ValueError
        except KeyError:
            raise ThrottleImproperlyConfigured('THROTTLE_ZONE[\'%s\'] missing NUM_BUCKETS parameter)' % zone_name)
        except ValueError:
            raise ThrottleImproperlyConfigured('THROTTLE_ZONE[\'%s\'][\'NUM_BUCKETS\'] must be >= 2' % zone_name)

        try:
            self.bucket_capacity = int(config['BUCKET_CAPACITY'])
        except KeyError:
            raise ThrottleImproperlyConfigured('THROTTLE_ZONE[\'%s\'] missing BUCKET_CAPACITY parameter)' % zone_name)
        except ValueError:
            raise ThrottleImproperlyConfigured('THROTTLE_ZONE[\'%s\'][\'BUCKET_CAPACITY\'] must be an int' % zone_name)

        self.bucket_span = self.bucket_interval * self.num_buckets

    def process_view(self, request, view_func, view_args, view_kwargs):
        # If THROTTLE_ENABLED is False, just return the response from the view.
        if not THROTTLE_ENABLED:
            return view_func(request, *view_args, **view_kwargs)

        # if func is a class view the request is the instance of the class
        view_class = request
        request = getattr(request, 'request', request)

        bucket_key = serialize_bucket_key(
            self.vary.get_bucket_key(request, view_func, view_args, view_kwargs)
        )

        # Calculate the bucket offset to increment
        timestamp = self.get_timestamp()
        bucket_num = int((timestamp % self.bucket_span) / self.bucket_interval)
        bucket_num_next = (bucket_num + 1) % self.num_buckets

        # Tell the backing store to increment the count
        new_value = get_backend().incr_bucket(self.name, bucket_key, bucket_num, bucket_num_next, self.bucket_span)

        # Has the bucket capacity been exceeded?
        if new_value > self.bucket_capacity:
            raise RateLimitExceeded(self.name)

        num_remaining = self.bucket_capacity - new_value

        # Execute the Django view. Add a few attributes to the response object.
        response = view_func(view_class, *view_args, **view_kwargs)
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


def _load_zone(zone_name, **config):
    vary_klass = load_class_from_path(config['VARY'])
    return ThrottleZone(zone_name, vary_klass, **config)


def get_zone(zone_name):
    try:
        return _THROTTLE_ZONES[zone_name]
    except KeyError:
        try:
            throttle_zone = settings.THROTTLE_ZONES[zone_name]
            zone = _load_zone(zone_name, **throttle_zone)
            _THROTTLE_ZONES[zone_name] = zone
            return zone
        except AttributeError:
            raise ImproperlyConfigured('@throttle is used, but settings.THROTTLE_ZONES is undefined')
        except KeyError:
            raise ThrottleZoneNotDefined(zone_name)
