from hashlib import sha256


class RemoteIP:
    def __init__(self, **config):
        pass

    def get_bucket_key(self, request, view_func, view_args, view_kwargs):
        """
        Return our best crack at the remote IP address
        """

        # Memcached can't take key with the spaces. This would be happen when
        #   you use more than one reverse proxy.
        return sha256(
            request.META.get('HTTP_X_FORWARDED_FOR', "") or request.META.get('REMOTE_ADDR')
        ).hexdigest()
