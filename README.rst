========================
django-throttle-requests
========================

*a framework for implementing rate-limiting middleware for Django projects*

|Build|  |PyVersion|  |PyPiVersion|  |License|

Overview
========

This package allows Django developers to define application-level rate-limiting rules. Often, these rules would be expressed as "max # requests within a defined time period". E.g.:

- an IP address may make at most 1500 requests/day

- users with an OAuth access token may make 500 reads/hour and 200 writes/hour

You can also define leaky bucket-style rules:

- Allow 10 requests per minute, then every 6 seconds thereafter.


Features
========

- Attach rules to specific views using a decorator
- Supports multiple throttle configurations
- Use Django's cache layer as the storage backend, or use Redis scripting for production-ready atomic operations
- Define request attributes to rate limit (e.g. remote IP address, username, HTTP header value, device fingerprint, etc.)
- Application-level rate limiting rules using fixed-bucket or generic cell rate algorithm (leaky bucket)



Installation
============

#. Install the library with pip::

    sudo pip install django-throttle-requests

#. Add the directory ``throttle`` to your project's ``PYTHONPATH``.

Usage
=====

#. Insert the following configuration into your project's settings::

    THROTTLE_ZONES = {
        'default': {
            'VARY':'throttle.zones.RemoteIP',
            'ALGORITHM': 'fixed-bucket',  # Default if not defined.
            'BUCKET_INTERVAL':15 * 60,  # Number of seconds to enforce limit.
            'BUCKET_CAPACITY':50,  # Maximum number of requests allowed within BUCKET_INTERVAL
        },
    }

    # Where to store request counts.
    THROTTLE_BACKEND = 'throttle.backends.cache.CacheBackend'

    # Optional if Redis backend is chosen ('throttle.backends.redispy.RedisBackend')
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

.. |Build| image:: https://github.com/sobotklp/django-throttle-requests/workflows/CI/badge.svg?branch=master
     :target: https://github.com/sobotklp/django-throttle-requests/actions?workflow=CI
     :alt: CI Status
