from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from throttle.utils import load_class_from_path

THROTTLE_BACKEND = getattr(settings, 'THROTTLE_BACKEND', {})
_backend = None

def load_backend_from_path(classpath):
    klass = load_class_from_path(classpath)
    try:
        return klass()
    except TypeError:
        raise ImproperlyConfigured("%s is not callable" % (klass.__name__))

def get_backend():
    global _backend
    if _backend:
        return _backend

    if THROTTLE_BACKEND:
        _backend = load_backend_from_path(settings.THROTTLE_BACKEND)
        return _backend
    else:
        raise ImproperlyConfigured('@throttle was used, but settings.THROTTLE_BACKEND is not set')