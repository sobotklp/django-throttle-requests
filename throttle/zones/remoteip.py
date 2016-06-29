class RemoteIP:
    def __init__(self, **config):
        pass

    def get_bucket_key(self, request, view_func, view_args, view_kwargs):
        """
        Return our best crack at the remote IP address
        """
        # Handle Load Balancer case
        # Load balancer returns usually in format of 'xx.xx.xx.xx, yy.yy.yy.yy, zz.zz.zz.zz'
        # where xx.xx.xx.xx is the actual ip while others vary on the request
        ip_string = request.META.get('HTTP_X_FORWARDED_FOR', "")
        ip_string = ip_string.split(',')[0]
        return ip_string or request.META.get('REMOTE_ADDR')
