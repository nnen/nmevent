# -*- encoding: utf-8 -*-
"""
Copyright (c) 2010, Jan Milík.
"""

__author__ = u"Jan Milík"
__all__    = ['with_events', 'EventSlot', 'Event', 'BoundEvent', 'EventArgs']

class EventArgs(object):
	"""
	Base class for event arguments objects.
	"""
	pass

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

	def has_handler(self, handler):
		"""Returns True if the specified handler is associated with this event."""
		return (handler in self.handlers)
	__contains__ = has_handler
	
	def fire(self, sender, *args, **keywords):
		"""Fires this event and calls all of its handlers."""
		for handler in self.handlers:
			handler(sender, *args, **keywords)
	__call__ = fire
	
	def disconnect(self):
		"""Disconnects this event from all handlers."""
		self.handlers = set()

class BoundEvent(object):
	def __init__(self, obj, event):
		self.obj   = obj
		self.event = event

	def __getattr__(self, name):
		return getattr(self.event, name)

	def __iadd__(self, handler):
		self.event += handler
		return self

	def __isub__(self, handler):
		self.event -= handler
		return self

	def __contains__(self, handler):
		return (handler in self.event)

	def __call__(self, *args, **keywords):
		self.event(self.obj, *args, **keywords)

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
		return BoundEvent(obj, event)

def with_events(clss):
	for name, attr in clss.__dict__.items():
		if not isinstance(attr, property):
			continue
		setattr(clss, name + "_changed", EventSlot())
	return clss

