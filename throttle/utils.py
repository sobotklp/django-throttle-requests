from hashlib import sha256

from django.core.exceptions import ImproperlyConfigured
try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module

def load_class_from_path(class_path):
    # Split the class into a <module, classname> pair
    try:
        modulename, classname = class_path.rsplit('.', 1)
    except ValueError:
        raise ImproperlyConfigured("'%s' isn't a valid module name" % (class_path))

    # Attempt to load the module
    try:
        module = import_module(modulename)
    except (ImportError,):
        raise ImproperlyConfigured("Error importing module '%s'" % (modulename))

    # Attempt to reference the class
    try:
        return getattr(module, classname)
    except AttributeError:
        raise ImproperlyConfigured("Module %s has no class '%s'" % (modulename, classname))

# Memcached can't take key with the spaces. This would be happen when
#   you use more than one reverse proxy.
def serialize_bucket_key(bucket_key):
    return sha256(bucket_key.encode('utf-8')).hexdigest()
