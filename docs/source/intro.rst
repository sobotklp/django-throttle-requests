.. _intro:

============
Introduction
============

In the context of web applications, limiting the number of requests a host or user makes solves two problems:

* withstanding Denial-of-service attacks (`rate-limiting <http://en.wikipedia.org/wiki/Rate_limiting>`_)
* ensuring that a user doesn't consume too many resources (throttling)

Rate-limiting is often accomplished with firewall rules on a device, ``iptables``, or web server. They are enforced at the network or transport layer before the request is delivered to the application. For example,
a rule such as "An IP address may make no more than 20 reqs/sec" would queue, or simply drop any requests that exceeded the maximum rate, and the application will not receive the request.

Throttling can be thought of as application middleware that maintains a count of users' requests during a specific time period. If an incoming request exceeds the maximum for the time period, the user receives a response (e.g. `HTTP 403 <http://en.wikipedia.org/wiki/HTTP_403>`_) containing a helpful error message.

A good example of throttling is `Twitter's controversial API rate-limiting <https://dev.twitter.com/docs/rate-limiting/1.1>`_. Twitter enforces several types of limits depending on the type of access token used and the API function used. An example of a rule is "a user may make no more than 150 requests per 15-minute window".

.. note::

    Although Twitter uses the term ``rate limiting``, I find it helpful to distinguish the concepts of network-layer rate limiting versus application-specific request limiting (throttling).