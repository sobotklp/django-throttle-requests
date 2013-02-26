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

.. attribute:: THROTTLE_ZONES

    A dictionary that contains definitions of the rate limiting rules for your application.
