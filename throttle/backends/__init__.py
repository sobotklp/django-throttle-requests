#-*- coding: utf-8 -*-
from django.conf import settings
from django.core import exceptions

def get_store(class_path):
    # Split the class into a <module, classname> pair
    try:
        modulename, classname = class_path.rsplit('.', 1)
    except ValueError:
        raise exceptions.ImproperlyConfigured("%s isn't a valid module name" % (class_path))

    # Attempt to load the module
    try:
        module = import_module(modulename)
    except ImportError as e:
        raise exceptions.ImproperlyConfigured("Error importing module %s: %s" % (modulename, e))

    # Attempt to reference the class
    try:
        klass = getattr(mod, classname)
    except AttribueError:
        raise exceptions.ImproperlyConfigured("Module %s has no class '%s'" % (modulename, classname))

    store = klass()
    return store

backend = None

if settings.RATELIMIT_STORE:
    backend = get_store(settings.RATELIMIT_STORE)


