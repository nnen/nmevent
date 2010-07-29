# -*- encoding: utf-8 -*-
# vim: expandtab:tabstop=4:softtabstop=4:autoindent

"""nmevent - C#-like implementation of the Observer pattern

This is a Python module "nmevent", simple C#-like implementation of
the Observer pattern (http://en.wikipedia.org/wiki/Observer_pattern).
It's main purpose and goal is to allow developers to use events
with C#-like syntax in their Python classes.

LICENSE

Copyright (c) 2010, Jan Milík.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope the it will be useful,
but WITHOUT ANY WARRANTY; without event the implied warranty of
MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = u"Jan Milik <milikjan@fit.cvut.cz>"
__all__    = ['with_events', 'EventSlot', 'Event', 'BoundEvent', 'EventArgs']

import __builtin__

class EventArgs(object):
    """Base class for event arguments objects.
    """

    def __init__(self, **keywords):
        self.keywords = keywords

    def __getattr__(self, name):
        if name in self.keywords:
            return self.keywords[name]

class Event(object):
    """Subject in the observer pattern.

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
        """Removes a handler from this event.

        Removes a handler (observer) from the collection of
        this event's handlers.
        """
        self.handlers.remove(handler)
        return self
    __isub__ = remove_handler

    def has_handler(self, handler):
        """Returns True if handler is this event's handler.
        
        Returns True if the specified handler is contained
        in the collection of this event's handlers.
        """
        return (handler in self.handlers)
    __contains__ = has_handler
    
    def fire(self, sender, *args, **keywords):
        """Fires this event and calls all of its handlers.
        """
        for handler in self.handlers:
            handler(sender, *args, **keywords)
    __call__ = fire
    
    def disconnect(self):
        """Disconnects this event from all handlers.
        """
        self.handlers = set()

class BoundEvent(object):
    """Event bound to an instance of an object.

    Bound event automatically uses the object it is
    bound to as its sender when raising the event.
    """

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
    """Event descriptor.
    """

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

class Property(object):
    """Eventful property descriptor.
    """

    @property
    def name(self):
        if self.fget is not None:
            return self.fget.__name__
        if self.fset is not None:
            return self.fset.__name__
        return None

    def __init__(self, fget = None, fset = None, fdel = None, changed = None, property_changed = None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel

        self.changed = changed
        self.property_changed = property_changed

    def __get__(self, obj, type = None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError, "Unreadable attribute."
        return self.fget(obj)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError, "Can't set attribute."
        self.fset(obj, value)
        self._fire(self.changed, obj)
        self._fire(self.property_changed, obj, name = self.name)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError, "Can't delete attribute."
        self.fdel(obj)

    def _fire(self, event, obj, **keywords):
        if isinstance(event, EventSlot):
            event.__get__(obj)(**keywords)
        elif isinstance(event, Event):
            event(obj, **keywords)

    def setter(self, function):
        self.fset = function
        return self

    def deleter(self, function):
        self.fdel = function
        return self

def property(function):
    return Property(function)

def with_events(clss):
    """Decorates a class with some automatic event slots.

    Automatically adds property change notification events
    of the name "x_changed", where x is the name of the
    property.
    """

    property_changed = EventSlot()
    setattr(clss, "property_changed", property_changed)

    for name, attr in clss.__dict__.items():
        if isinstance(attr, __builtin__.property):
            setattr(clss, name + "_changed", EventSlot())
        elif isinstance(attr, Property):
            slot = EventSlot()
            setattr(clss, name + "_changed", slot)
            attr.changed = slot
            attr.property_changed = property_changed
    return clss

