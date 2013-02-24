class ThrottleBackendBase:
    def incr_bucket(self, zone_name, bucket_key, bucket_num, bucket_num_next, bucket_span, cost=1):
        """
        Increments the limit for the given bucket.

        @returns: the new value of the bucket, post-increment
        """
        raise NotImplementedError
