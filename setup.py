#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup
try:
    import multiprocessing # Suppresses a confusing but harmless warning when running ./setup.py test
    import logging
except ImportError:
    # multiprocessing introduced in Python 2.6
    pass

from throttle import __version__

long_description = open('README.rst').read()

setup(
    name="django-throttle-requests",
    description="A Django framework for application-layer rate limiting",
    long_description=long_description,
    packages=find_packages(),
    url="https://github.com/sobotklp/django-throttle-requests",
    version=__version__,
    author='Lewis Sobotkiewicz',
    author_email='lewis.sobot@gmail.com',
    install_requires=[
        'Django>=1.6',
    ],
    test_suite='runtests.runtests',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
