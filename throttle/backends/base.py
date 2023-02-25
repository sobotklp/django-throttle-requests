class ThrottleBackendBase:
    def incr_bucket(self, zone_name, bucket_key, bucket_interval, limit, cost=1):
        """
        Increments the limit for the given bucket.

        @returns: the new value of the bucket, post-increment
        """
        raise NotImplementedError

    def gcra(self, zone_name, bucket_key, bucket_interval, limit):
        """
        Increments the limit for the given bucket.

        @returns: the new value of the bucket, post-increment
        """
        raise NotImplementedError

    def get_algorithm(self, algorithm_name):
        """
        Returns a reference to the method implementing `algorithm_name`
        """
        raise NotImplementedError
