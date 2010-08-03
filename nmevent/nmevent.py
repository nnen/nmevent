# -*- encoding: utf-8 -*-
# vim: expandtab:tabstop=4:softtabstop=4:autoindent

"""nmevent - C#-like implementation of the Observer pattern

This is a Python module :mod:`nmevent`, simple C#-like implementation of
the Observer pattern (http://en.wikipedia.org/wiki/Observer_pattern).
It's main purpose and goal is to allow developers to use events
with C#-like syntax in their Python classes.

Usage example
=============

The most straightfoward way to use :mod:`nmevent` is this:

>>> import nmevent
>>> class ExampleClass(object):
...    def __init__(self):
...       self.event = nmevent.Event()
...
...    def _do_something(self):
...       self.event(self)
...
>>> example = ExampleClass()
>>> example.event += handler

It should be noted, that event doesn't necessarily need to
be an object attribute. :class:`Event` instance is basically
just a callable object that works as a sort of "dispatch
demultiplexer".

This usage, however, isn't very C#-like. In C#, events are declared
in class scope and that's where the :class:`EventSlot` comes in.
Once you've created event using :class:`EventSlot`, you can
use the same way you use :class:`Event`, only you don't need
to specify the sender when raising the event. That's because
the event is already bound to the instance of the class it has
been declared in.

>>> from nmevent import EventSlot
>>> class ExampleClass(object):
...    event = EventSlot()
...
...    def _do_something(self):
...       self.event()
...
>>> def handler(sender, **keywords):
...    pass
...
>>> example = ExampleClass()
>>> example.event += handler

Perhaps this looks even more straightfoward than instantiating
:class:`Event` in object's constructor, but there's actually
lot more going on under hood this time.

>>> import nmevent
>>> @nmevent.with_events
... class ExampleClass(object):
...    @nmevent.nmproperty
...    def x(self):
...       return self._x
...
>>> example = ExampleClass()
>>> example.x_changed += handler
>>> example.x = 10 # handler gets called

License
=======

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
__all__    = [
    'nmproperty',
    'with_events',
    'EventSlot',
    'Event',
    'EventArgs',
]

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

    >>> class Example(object):
    ...    def __init__(self):
    ...       self.event = Event()
    ...
    ...    def fire(self):
    ...       self.event(self)
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
    This class is not to be used directly by the client
    code; instances of this class are created by
    the :class:`EventSlot` class.

    The difference between :class:`Event` and :class:`EventSlot`
    is somewhat similar to the difference between python's
    functions and bound methods (bound method automatically
    passes the object it is bound to to the function it envelopes
    as the first argument).

    Usage:

    >>> instance += handler
    >>> instance -= handler
    >>> handler in instance
    >>> instance(*args, **keywords)
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

    This is an event descriptor, which means it works
    kind of like the built-in property object. You can
    find more information on descriptors in Python's
    documentation (http://docs.python.org/reference/datamodel#customizing-attribute-access),
    or in a number of articles such as Raymond Hettinger's
    how-to (http://users.rcn.com/python/download/Descriptor.htm).
    In short, as the Python documentation puts it, descriptor
    is an object with "binding behavior".

    The rationale for this class is that, unlike the :class:`Event`
    class alone, it alows client to declare events in the class scope.
    The events don't need the ``__init__()`` method to be run in order
    to be instantiated. This is especially helpfull when using inheritance,
    because the inherited class doesn't need to explicitly call base
    class's constructor in order to inherit the events.

    Also, declaring the events in the class scope is more C#-like
    than instantiating them in the constructor.

    Usage:

    >>> class Example(object):
    ...    something_changed = EventSlot()
    ...
    ...    def foo(self):
    ...       self.something_changed()
    ...
    >>> example = Example()
    >>> example.something_changed += handler
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

    This class is not meant to be used directly by the
    client code, even though nothing stops you from
    doing so. Instances of this class are supposed to
    be created by the :func:`nmproperty` decorator.

    :param fget: getter function
    :param fget: getter function
    :param fset: setter function
    :param fdel: deleter function
    :param changed: value changed notification event
    :param property_changed: a value changed notification event

    Usage:

    >>> class Example(object):
    ...    @nmproperty:
    ...    def x(self):
    ...       return self._x
    ...
    ...    @x.setter
    ...    def x(self, value):
    ...       self._x = value
    ...
    >>> example = Example()
    >>> exmaple.x_changed += handler
    >>> example.x = 42

    .. attribute:: fget
       
       Getter function.

       If non-None, this function gets called every time
       the value of the property is retrieved. The return
       value of this function is returned as the value of
       the property.

    .. attribute:: fset
       
       Setter function.

       If non-None, this function gets called every time
       the value of the property is set. This function
       is responsible for actually storing the value somehow.
       
       If this attribute is ``None``, the property is considered
       read-only.

    .. attribute:: fget
       
       Deleter function.

    .. attribute:: changed
       
       Value change notification event.

       If non-None, this event will be raised every time
       this property is set to a different value.

    .. attribute:: property_changed
       
       Property value change notification event.
       
       If none-None, this event will be raised every time
       this property is set to a different value. Unlike
       the :attr:`~Property.changed` event, however, the
       handlers of this event will also be passed keyword
       ``name``, which will contain the name of this property
       (see :attr:`Property.name`).

       This is can be used when you need to watch for change
       of any property, but need to know which one changed.

       This event has been inspired by the .NET framework's
       ``INotifyPropertyChanged`` interface (see
       http://msdn.microsoft.com/en-US/library/system.componentmodel.inotifypropertychanged.aspx)
    """

    @property
    def name(self):
        """The name of the property.

        This should be the name of an object's attribute
        that holds the property. The name is guessed by
        retrieving the name of the getter function if present.
        """
        if self.fget is not None:
            return self.fget.__name__
        return None

    def __init__(self, fget = None, fset = None, fdel = None,
                 changed = None, property_changed = None):
        """Constructor."""
        self.fget = fget
        self.fset = fset
        self.fdel = fdel

        self.changed = changed
        self.property_changed = property_changed

    def __get__(self, obj, objtype = None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError, "Unreadable attribute."
        return self.fget(obj)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError, "Can't set attribute."
        if self.fget is None:
            self.fset(obj, value)
            return
        old_value = self.fget(obj)
        self.fset(obj, value)
        if old_value != value:
            self._fire(self.changed, obj, old_value = old_value)
            self._fire(self.property_changed, obj, old_value = old_value, name = self.name)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError, "Can't delete attribute."
        self.fdel(obj)

    def _fire(self, event, obj, **keywords):
        """Propety._fire(event, obj, **keywords) - private helper function.
        """
        if isinstance(event, EventSlot):
            event.__get__(obj)(**keywords)
        elif isinstance(event, Event):
            event(obj, **keywords)

    def setter(self, function):
        """Sets the setter function and returns self.

        This function is meant to be used as a method decorator,
        even though it can be called directly to set the
        setter function of its property.

        Usage:

        >>> class ExampleClass(object):
        ...    def x(self):
        ...       return self._x
        ...
        ...    # @nmevent.nmproperty could have been used,
        ...    # but this way it is more obvious what x is.
        ...    x = nmevent.Property(x)
        ...
        ...    # This is how it's supposed to be used.
        ...    @x.setter
        ...    def set_x(self, value):
        ...       self._x = value
        ...
        ...    # Also works, but looks ugly.
        ...    x.setter(set_x)
        ...

        :param function: the property setter function
        :returns: self
        """
        self.fset = function
        return self

    def deleter(self, function):
        """Property.deleter(function) - method decorator te set the delete function.

        Works exatcly like the built-in @property.deleter.
        
        :param function: the property deleter function
        :returns: self
        """
        self.fdel = function
        return self

def nmproperty(function):
    """Eventful property decorator.

    Creates new :class:`Property` object using the decorated method
    as the getter function. Setter and deleter functions can be
    set by the :meth:`Property.setter` and :meth:`Property.deleter`
    decorators where "name" is the name of the property (the name
    of the getter function).

    This decorator is called :func:`nmproperty` to avoid name conflict
    with the built-in `property` function and decorator.

    Usage:

    >>> class ExampleClass(object):
    ...    @nmevent.nmproperty
    ...    def x(self):
    ...       return self._x
    ...    
    ...    @x.setter
    ...    def x(self, value)
    ...       self._x = value
    ...
    ...    x_changed = EventSlot
    ...    x.changed = x_changed
    ...
    >>> example = ExampleClass()
    >>> example.x_changed += handler # "handler" will be called when the value of x changes
    >>> example.x = 10 # value of x changed, "handler" should get called

    The changed events can be automatically created and set
    by the :func:`with_events` decorator.

    :param function: function to be used as the property getter function
    :returns: new `Property` object
    """
    return Property(function)

def with_events(clss):
    """Decorates a class with some automatic event slots.

    Automatically adds property change notification events
    of the name "x_changed", where x is the name of the
    property.

    :param clss: class object to be decorated
    :returns: decorated class
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

