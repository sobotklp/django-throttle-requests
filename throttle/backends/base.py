class ThrottleBackendBase:
    def incr_bucket(self, zone_name, bucket_key, bucket_num, bucket_num_next):
        """
        Increments the limit for the given bucket.

        @returns: the new value of the bucket, post-increment
        """
        raise NotImplementedError


