import time

class ThrottleBackendBase(object):
    def __init__(self):
        self.get_timestamp = lambda: int(time.time())

    def _params(self, strategy, *args, **kwargs):
        # Calculate the bucket to increment
        timestamp = self.get_timestamp()
        bucket_num = (timestamp % self.bucket_span) / self.bucket_interval

        self.test_limit(strategy, timestamp, *args, **kwargs)

    def test_limit(self, strategy, timestamp, *args, **kwargs):
        raise NotImplementedError


