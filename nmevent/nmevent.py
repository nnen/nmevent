# -*- encoding: utf-8 -*-
"""
Copyright (c) 2010, Jan Milík.
"""

__author__ = u"Jan Milík"
__all__    = ['EventSlot', 'Event', 'EventArgs']

class EventSlot(object):
	EVENTS_ATTRIBUTE = '__events__'

	def __get__(self, obj, objtype = None):
		if obj is None:
			return self
		events = obj.__dict__.get(self.EVENTS_ATTRIBUTE, None)
		if events is None:
			events = {}
			obj.__dict__[self.EVENTS_ATTRIBUTE] = events
		event = events.get(id(self), None)
		if event is None:
			event = Event()
			events[id(self)] = event
		return event

class Event(object):
	"""
	This class represents the subject in the observer pattern.
	It keeps a collection of handlers, which correspond to the
	observers in the observer pattern.

	Usage:

	>>> class Klass(object):
	...    def __init__(self):
	...       self.event1 = Event()
	...       self.event2 = Event()
	...
	...    def fire(self):
	...       self.event1(self)
	...
	"""

	def __init__(self):
		self.handlers = set()
	
	def add_handler(self, handler):
		"""Adds a handler (observer) to this event."""
		self.handlers.add(handler)
		return self
	__iadd__ = add_handler
	
	def remove_handler(self, handler):
		"""Removes a handler (observer) from the collection of
		this event's handlers."""
		self.handlers.remove(handler)
		return self
	__isub__ = remove_handler
	
	def fire(self, sender, *args, **keywords):
		"""Fires this event. Calls all the handlers with the
		arguments and keywords."""
		for handler in self.handlers:
			handler(sender, *args, **keywords)
	__call__ = fire
	
	def disconnect(self):
		"""Clears this event's handler collection. Removes
		all handlers."""
		self.handlers = set()

class EventArgs(object):
	"""
	Base class for event arguments objects.
	"""
	pass

