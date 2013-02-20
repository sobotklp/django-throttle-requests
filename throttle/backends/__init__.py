from django.core.exceptions import ImproperlyConfigured

from throttle.utils import load_class_from_path

def get_backend(class_path):
    klass = load_class_from_path(class_path)

    try:
        return klass()
    except TypeError:
        raise ImproperlyConfigured("%s is not callable" % (klass.__name__))
