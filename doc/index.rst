.. nmevent documentation master file, created by
   sphinx-quickstart on Tue Aug  3 00:13:33 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to nmevent's documentation!
===================================

.. toctree::
   :maxdepth: 2

.. automodule:: nmevent

``nmevent`` module
==================

.. attribute:: nmevent.EVENTS_ATTRIBUTE
   
   Value of this module variable is the name of the attribute
   that is used to store event data in object instances when
   :class:`Event` is used as an descriptor. 
   
   If the class of your object uses the ``__slots__`` attribute,
   don't forget to include the value of this variable in the
   sequence you assign to ``__slots__``.
   
   Example:
   
   >>> class Example(object):
   ...    __slots__ = ('foo', 'bar', nmevent.EVENTS_ATTRIBUTE, )
   ...    event = nmevent.Event()

Types
-----

.. autoclass:: nmevent.Event
	:members:

.. autoclass:: nmevent.InstanceEvent
	:members:

.. autoclass:: nmevent.Property
	:members:

Functions
---------

.. autofunction:: nmevent.nmproperty
.. autofunction:: nmevent.with_events

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

