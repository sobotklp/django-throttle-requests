===============
django-throttle
===============

*a framework for implementing application-specific rate-limiting middleware for Django projects*

.. image:: https://travis-ci.org/sobotklp/django-throttle.png?branch=master
   :alt: Built Status
   :target: http://travis-ci.org/sobotklp/django-throttle



What this module is intended for:
=================================

Implementing application-level (or just below) rate limiting, with the ability to create rules such as:

* an IP address may make at most 1500 requests/day

* users with an OAuth access token may make 500 reads/hour and 200 writes/hour


What it is not intended for:
============================

A token bucket or leaky bucket filter: those algorithms are intended primarily for traffic shaping, and are already well-served by using ``nginx`` or one of its peers as a frontend to your app. Also, those algorithms require a single, high-granularity system-wide timer to implement leaking - that would make distributing the algorithm much more difficult.

Installation
============

#. Add the director ``throttle`` to your project's ``PYTHONPATH``.

#. Insert the following configuration into your project's settings::

    THROTTLE_ZONES = {
        'default': {
            'VARY':'throttle.zones.RemoteIP',
            'NUM_BUCKETS':2, # Number of buckets worth of history to keep. Must be at least 2
            'BUCKET_CAPACITY':50, # Maximum number of requests allowed within BUCKET_INTERVAL
            'BUCKET_INTERVAL':15 * 60 # Number of seconds to use each bucket.
        },
    }

    # Where to store request counts.
    THROTTLE_BACKEND = 'throttle.backends.cache.CacheBackend'

    # Force throttling, even when DEBUG=True
    THROTTLE_ENABLED = True

#. Use the ``@throttle`` decorator to enforce throttling rules on a view::

    @throttle(zone='default')
    def myview(request):
       ...

:Code:          https://github.com/sobotklp/django-throttle-requests
