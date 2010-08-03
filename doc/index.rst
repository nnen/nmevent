.. nmevent documentation master file, created by
   sphinx-quickstart on Tue Aug  3 00:13:33 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to nmevent's documentation!
===================================

.. toctree::
   :maxdepth: 2

.. automodule:: nmevent

Types
=====

.. autoclass:: nmevent.Event
	:members:

.. autoclass:: nmevent.EventSlot
	:members:

Functions
=========

.. autofunction:: nmevent.nmproperty
.. autofunction:: nmevent.with_events

Other types
===========

These types are not meant to be used by the client code directly.
That is why they are not listed in the module's ``__all__`` attribute
and will not be imported when doing ``from nmevent import *``.
However, nothing really stops you from using them if you insist on it.

The types below are documented here only to give you a better idea
about what's going on.

.. autoclass:: nmevent.BoundEvent
	:members:

.. autoclass:: nmevent.Property
	:members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

