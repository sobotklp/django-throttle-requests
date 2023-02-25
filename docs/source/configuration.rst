.. _configuration:

=============
Configuration
=============

.. currentmodule:: django.conf.settings

.. attribute:: THROTTLE_ENABLED

    :default: not ``settings.DEBUG``

    Optional boolean value that is used to control whether or not throttling is enforced. To test throttling
    when ``DEBUG`` is ``True``, you must also explicitly set ``THROTTLE_ENABLED = True``.

.. attribute:: THROTTLE_BACKEND

    The path to the class that implements the backend storage mechanism for per-user request counts.
    Currently, only two values are supported:

    ``throttle.backends.cache.CacheBackend`` uses Django's cache backend for storage. If you're going to use this in production, ensure that your cache backend supports atomic increment operations.
    ``throttle.backends.redispy.RedisBackend`` uses ``redispy`` and Lua scripting to perform operations atomically within Redis. This is the recommended backend for high-volume production use.

.. attribute:: THROTTLE_ZONES

    A dictionary that contains definitions of the rate limiting rules for your application.
