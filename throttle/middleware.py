from exceptions import RateLimitExceeded


class RateLimitMiddleware:
    def process_exception(self, request, exception):
        if not isinstance(exception, RateLimitExceeded):
            return
