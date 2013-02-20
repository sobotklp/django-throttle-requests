django-throttle - a framework for implementing application-level rate-limiting middleware for Django projects

.. image:: https://travis-ci.org/sobotklp/django-throttle.png?branch=master
   :alt: Built Status
   :target: http://travis-ci.org/sobotklp/django-throttle

What this module is intended for::

    implementing application-level (or just below) rate limiting, with the ability to create rules such as:
        - an IP address may make at most 1500 requests/day
        - users with an OAuth access token may make 500 reads/hour and 200 writes/hour


What it is not intended for::

    a token bucket or leaky bucket filter: those algorithms are intended primarily for traffic shaping, and are already well-served by using ``nginx`` or one of its peers as a frontend to your app. Also, those algorithms require a single, high-granularity system-wide timer to implement leaking - that would make distributing the algorithm much more difficult.

Installation
============

TODO

