from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

def get_backend(class_path):
    # Split the class into a <module, classname> pair
    try:
        modulename, classname = class_path.rsplit('.', 1)
    except ValueError:
        raise ImproperlyConfigured("%s isn't a valid module name" % (class_path))

    # Attempt to load the module
    try:
        module = import_module(modulename)
    except ImportError as e:
        raise ImproperlyConfigured("Error importing module %s: %s" % (modulename, e))

    # Attempt to reference the class
    try:
        klass = getattr(module, classname)
    except AttributeError:
        raise ImproperlyConfigured("Module %s has no class '%s'" % (modulename, classname))

    try:
        store = klass()
    except TypeError as e:
        raise ImproperlyConfigured("%s is not callable" % (klass.__name__))

    return store
