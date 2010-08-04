# -*- encoding: utf-8 -*-
# vim: expandtab:tabstop=4:softtabstop=4:autoindent

"""nmevent v0.2 - C#-like implementation of the Observer pattern

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

It should be noted, that event doesn't necessarily need to be an object
attribute. :class:`Event` instance is basically just a callable object that
works as a sort of "dispatch demultiplexer".

This usage, however, isn't very C#-like. In C#, events are declared in class
scope and that's why the :class:`Event` class also supports the descriptor
protocol (you can use the same way you use the built-in ``property`` object).

>>> from nmevent import EventSlot
>>> class ExampleClass(object):
...    event = Event()
...
...    def _do_something(self):
...       self.event()
...
>>> def handler(sender, **keywords):
...    pass
...
>>> example = ExampleClass()
>>> example.event += handler

Perhaps this looks even more straightfoward than instantiating :class:`Event`
in object's constructor, but there's actually lot more going on under hood this
time.

Finally, there is the :class:`Property` descriptor and the associated
:func:`nmproperty` function decorator, which work very much like the built-in
``property`` object and decorator, except it can optionally call a callback
function if the property's value changes after calling the setter function. It
can work in tandem with the :func:`with_events` class decorator, which
decorates the class with property change events and connects them to the
instances of :class:`Property` class. It also creates events for the built-in
``property`` objects, but you have to raise the events yourself in the setter
function or elsewhere.

>>> import nmevent
>>> @nmevent.with_events
... class ExampleClass(object):
...    @nmevent.nmproperty
...    def x(self):
...       return self._x
...
...    @x.setter
...    def x(self, value):
...       self._x = value
...
...    @property
...    def y(self):
...       return self._y
...
...    @y.setter
...    def y(self, value):
...       old_value, self._y = self._y, value
...       self.y_changed(old_value = old_value)
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

__version__ = __doc__.splitlines()[0].split(' ')[1][1:]
__author__ = u"Jan Milik <milikjan@fit.cvut.cz>"
__all__    = [
    'nmproperty',
    'with_events',
    'Event',
]

import __builtin__

EVENTS_ATTRIBUTE = '__nmevents__'

class CallbackStore(object):
    def __init__(self):
        self.callbacks = set()

    def __iter__(self):
        return iter(self.callbacks)

    def add(self, callback):
        self.callbacks.add(callback)
        return self
    __iadd__ = add

    def remove(self, callback):
        self.callbacks.remove(callback)
        return self
    __isub__ = remove

    def contains(self, callback):
        return callback in self.callbacks
    __contains__ = contains

    def count(self):
        return len(self.callbacks)
    __len__ = count

    def clear(self):
        self.callbacks = set()

    def call(self, *args, **keywords):
        for callback in self.callbacks:
            callback(*args, **keywords)
    __call__ = call

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

    __slots__ = ('__handlers__', )

    @property
    def handlers(self):
        if self.__handlers__ is None:
            self.__handlers__ = CallbackStore()
        return self.__handlers__
        
    def __init__(self):
        self.__handlers__ = None

    def __get__(self, obj, objtype = None):
        return self.bind(objtype, obj)

    def __set__(self, obj, value):
        # raise AttributeError, "Events are read-only attributes."
        pass

    def __delete__(self, obj):
        raise AttributeError, "Events are read-only attributes."

    def bind(self, objtype, obj = None):
        """Binds the event to a class and optionally an instance."""
        return InstanceEvent(self, objtype, obj)
    
    def add_handler(self, handler):
        """Adds a handler (observer) to this event.

        ``__iadd__`` attribute of this class is just an alias of this
        method, so the two following statements are equivalent:

        >>> event.add_handler(handler)
        >>> event += handler
        """
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
        self.handlers.call(sender, *args, **keywords)
    __call__ = fire
    
    def disconnect(self):
        """Disconnects this event from all handlers.
        """
        self.handlers.clear()

class InstanceEvent(object):
    """Bound or unbound event.

    In Python, unbound actually means bound to a class.
    Bound means bound to both a class and an instance.
    Instances of this class cannot be bound to the 
    ``None`` object, because it is used to indicate
    that the event is unbound.

    This class is meant to be instantiated either through
    the :class:`Event`'s descriptor protocol, or by
    the :meth:`Event.bind` method.

    :param event: :class:`Event` instance to be bound
    :param clss: class the event should be bound to (sender must be of this type)
    :param sender: sender to bind the event to

    .. attribute:: __slots__
       
       This class uses the ``__slots__`` attribute to save
       memory, so don't try to assign new attributes to
       its instances.

    .. attribute:: im_event
       
       :class:`Event` instance that is bound.

    .. attribute:: im_class

       Class object this event is bound to.

    .. attribute:: im_sender

       Instance this event is bound to.

       The following condition must be always true:

       >>> isinstance(self.im_sender, self.im_class)
    """
    
    __slots__ = ('im_event', 'im_class', 'im_sender', )

    @property
    def is_bound(self):
        """``True`` if the event is bound to a sender, ``False`` otherwise."""
        return bool(self.im_sender is not None)

    @property
    def handlers(self):
        if not self.is_bound:
            return self.im_event.handlers
        
        sender = self.im_sender
        if sender is None:
            return None
        
        events = sender.__dict__.setdefault(EVENTS_ATTRIBUTE, {})
        handlers = events.setdefault(id(self.im_event), CallbackStore())

        return handlers

    def __init__(self, event, clss, sender = None):
        self.im_event = event
        self.im_class = clss
        self.im_sender = sender
    
    def __call__(self, *args, **keywords):
        sender = self.im_sender
        if sender is None:
            if len(args) < 1:
                raise TypeError, ("Unbound event must be called with "
                    "at least 1 positional argument representing the sender.")
            if type(args[0]) is not self.im_class:
                raise TypeError, ("This unbound event must be called with "
                    "%s instance as the first argument." % (self.im_class.__name__))
            sender = args[0]
            args = args[1:]
        return self.handlers(sender, *args, **keywords)

    def __iadd__(self, handler):
        if self.is_bound:
            self.handlers.add(handler)
        else:
            self.im_event += handler
        return self

    def __isub__(self, handler):
        if self.is_bound:
            self.handlers.remove(handler)
        else:
            self.im_event -= handler
        return self

    def __contains__(self, handler):
        if self.is_bound:
            return handler in self.handlers
        else:
            return handler in self.im_event

    def __getattr__(self, name):
        return getattr(self.im_event, name)

    def __str__(self):
        if self.is_bound:
            return "<bound event>"
        return "<unbound event>"
    
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
            if self.changed is not None:
                self.changed(old_value = old_value)
            if self.property_changed is not None:
                self.property_changed(old_value = old_value, name = self.name)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError, "Can't delete attribute."
        self.fdel(obj)

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
    decorators.

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

    The :attr:`Property.changed` events can be automatically created and set
    by the :func:`with_events` decorator when used on the class.

    :param function: function to be used as the property getter function
    :returns: new `Property` object
    """
    return Property(function)

def with_events(clss):
    """Decorates a class with some automatic event slots.

    :param clss: class object to be decorated
    :returns:    decorated class

    Automatically adds property change notification events of the name
    "x_changed", where x is the name of the property.

    Usage:

    >>> @nmevent.with_events
    ... class Example(object):
    ...    @nmevent.nmproperty
    ...    def x(self):
    ...       return self._x
    ...
    ...    @x.setter
    ...    def x(self, value):
    ...       self._x
    ...
    ...    def __init__(self):
    ...       self._x = 0
    ...
    >>> def x_changed_handler(self, sender, **keywords):
    ...    old_value = keywords['old_value']
    ...    print "x changed; %r -> %r" % (old_value, sender.x)
    ...
    >>> def property_changed_handler(self, sender, **keywords):
    ...    old_value = keywords['old_value']
    ...    name = keywords['name']
    ...    print "property \"%s\" changed, %r -> %r" % (old_value, sender.x)
    ...
    >>> example = Example()
    >>> example.x_changed += x_changed_handler
    >>> example.property_changed_handler += property_changed_handler
    >>> example.x = 42

    In the example above, the :func:`with_events` decorator automatically
    decorates the class with an ``x_changed`` event and ``property_changed``
    event connects them to the instance of :class:`Property` class created by
    the :func:`nmproperty` decorator.

    Simply put, the class has ``x_changed`` event and ``property_changed``
    events that are raised when the value of ``Example.x`` changes.
    ``x_changed`` gets called only when ``Example.x`` changes,
    ``property_changed`` gets called when any property changes.
    """

    property_changed = Event()
    setattr(clss, "property_changed", property_changed)

    for name, attr in clss.__dict__.items():
        if isinstance(attr, __builtin__.property):
            setattr(clss, name + "_changed", Event())
        elif isinstance(attr, Property):
            slot = Event()
            setattr(clss, name + "_changed", slot)
            attr.changed = slot
            attr.property_changed = property_changed
    return clss

