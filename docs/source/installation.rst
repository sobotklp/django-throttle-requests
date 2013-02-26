.. _install:

============
Installation
============

#. Install the library with pip::

    sudo pip install django-throttle-requests

#. Add the directory ``throttle`` to your project's ``PYTHONPATH``.

#. Insert the following configuration into your project's settings::

    THROTTLE_ZONES = {
        'default': {
            'VARY':'throttle.zones.RemoteIP',
            'NUM_BUCKETS':2,  # Number of buckets worth of history to keep. Must be at least 2
            'BUCKET_INTERVAL':15 * 60  # Period of time to enforce limits.
            'BUCKET_CAPACITY':50,  # Maximum number of requests allowed within BUCKET_INTERVAL
        },
    }

    # Where to store request counts.
    THROTTLE_BACKEND = 'throttle.backends.cache.CacheBackend'

    # Force throttling when DEBUG=True
    THROTTLE_ENABLED = True

#. Use the ``@throttle`` decorator to enforce throttling rules on a view::

    from throttle.decorators import throttle

    @throttle(zone='default')
    def myview(request):
       ...
