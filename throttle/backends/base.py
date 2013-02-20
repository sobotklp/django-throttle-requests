import time

# For tests, we'll want to be able to mock this out.
get_timestamp = lambda: int(time.time()) 

class RateLimitBackendBase(object):
    def __init__(self, bucket_span, bucket_interval):
        self.bucket_span = bucket_span
        self.bucket_interval = bucket_interval

    def _params(self, strategy, *args, **kwargs):
        # Calculate the bucket to increment
        timestamp = get_timestamp()
        bucket_num = (timestamp % self.bucket_span) / self.bucket_interval

        self.test_limit(strategy, timestamp, *args, **kwargs)

    def test_limit(self, strategy, timestamp, *args, **kwargs):
        raise NotImplementedError


