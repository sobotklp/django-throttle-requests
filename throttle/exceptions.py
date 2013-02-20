from django.core.exceptions import ImproperlyConfigured, PermissionDenied

class RateLimitExceeded(PermissionDenied):
    pass

class ThrottleZoneNotDefined(ImproperlyConfigured):
    pass

