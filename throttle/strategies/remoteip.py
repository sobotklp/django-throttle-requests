class RemoteIP:
    def process_request(self, request):
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR', "") or request.META.get('REMOTE_ADDR')
        return ip_address

