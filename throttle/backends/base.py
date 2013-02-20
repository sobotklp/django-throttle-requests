import time

class ThrottleBackendBase(object):
    def __init__(self):
        self.get_timestamp = lambda: int(time.time())

    def test_limit(self, zone_name, bucket_key, bucket_num, *args, **kwargs):
        """
        Increments the limit for the given bucket.

        @returns: the new value of the bucket, post-increment
        """
        raise NotImplementedError


