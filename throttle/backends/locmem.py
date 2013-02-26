import threading

from base import ThrottleBackendBase

class LocMemBackend(ThrottleBackendBase):
    """
    A backend that uses the server's local memory to store throttling buckets

    This backend is not intended to be used for production purposes.
    """
    def incr_bucket(self, zone_name, bucket_key, bucket_num, bucket_num_next, bucket_span, cost=1):
        pass

