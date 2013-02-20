class ThrottleBackendBase:
    def test_limit(self, zone_name, bucket_key, bucket_num):
        """
        Increments the limit for the given bucket.

        @returns: the new value of the bucket, post-increment
        """
        raise NotImplementedError


