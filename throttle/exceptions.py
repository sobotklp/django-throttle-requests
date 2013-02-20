# -*- coding: utf-8 -*-
from django.core.exceptions import ImproperlyConfigured, PermissionDenied

class RateLimitExceeded(PermissionDenied):
    pass

class RateLimiterNotDefined(ImproperlyConfigured):
    pass

