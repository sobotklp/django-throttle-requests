========================
django-throttle-requests
========================

*a framework for implementing application-specific rate-limiting middleware for Django projects*

|Build|  |PyVersion|  |PyPiVersion|  |License|


What this module is intended for:
=================================

Implementing application-level (or just below) rate-limiting rules. Often, these rules would be expressed as "max # requests within a defined time period". E.g.:

* an IP address may make at most 1500 requests/day

* users with an OAuth access token may make 500 reads/hour and 200 writes/hour


What it is not intended for:
============================

A token bucket or leaky bucket filter: intended primarily for traffic shaping, those algorithms are implemented by firewalls and servers such as ``nginx``.

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
            'BUCKET_INTERVAL':15 * 60,  # Period of time to enforce limits.
            'BUCKET_CAPACITY':50,  # Maximum number of requests allowed within BUCKET_INTERVAL
        },
    }

    # Where to store request counts.
    THROTTLE_BACKEND = 'throttle.backends.cache.CacheBackend'

    # Optional after Redis backend is chosen ('throttle.backends.redispy.RedisBackend')
    THROTTLE_REDIS_HOST = 'localhost'
    THROTTLE_REDIS_PORT = 6379
    THROTTLE_REDIS_DB = 0  
    THROTTLE_REDIS_AUTH = 'pass'
    
    # Normally, throttling is disabled when DEBUG=True. Use this to force it to enabled.
    THROTTLE_ENABLED = True

#. Use the ``@throttle`` decorator to enforce throttling rules on a view::

    from throttle.decorators import throttle

    @throttle(zone='default')
    def myview(request):
       ...

#. Also works with class-based views::

    from django.views.generic import View
    from django.utils.decorators import method_decorator

    from throttle.decorators import throttle

    class TestView(View):

        @method_decorator(throttle(zone='default'))
        def dispatch(self, *args, **kwargs):
            return super(TestView, self).dispatch(*args, **kwargs)

        def head(self, request):
            ...

        def get(self, request):
            ...

:Code:          https://github.com/sobotklp/django-throttle-requests
:Documentation: https://readthedocs.org/projects/django-throttle-requests/

.. |PyPiVersion| image:: https://img.shields.io/pypi/v/django-throttle-requests.svg
   :alt: PyPi
   :target: https://pypi.python.org/pypi/django-throttle-requests

.. |License| image:: https://img.shields.io/badge/license-MIT-yellow.svg
   :alt:

.. |PyVersion| image:: https://img.shields.io/badge/python-2.7+-blue.svg
   :alt:

.. |Build| image:: https://secure.travis-ci.org/sobotklp/django-throttle-requests.png?branch=master
    :alt: Build Status
    :target: http://travis-ci.org/sobotklp/django-throttle-requests
