# -*- encoding: utf-8 -*-
# vim: expandtab:tabstop=4:shiftwidth=4:softtabstop=4:autoindent

"""nmevent v0.3.1 - C#-like implementation of the Observer pattern

This is a Python module :mod:`nmevent`, simple C#-like implementation of
the Observer pattern (http://en.wikipedia.org/wiki/Observer_pattern).
It's main purpose and goal is to allow developers to use events
with C#-like syntax in their Python classes.

=============
Usage example
=============

The most straightfoward way to use :mod:`nmevent` is this:

>>> import nmevent
>>> class ExampleClass(object):
...    def __init__(self):
...       self.event = nmevent.Event()
... 
...    def do_something(self):
...       self.event(self)
...
>>> def handler(sender, **keywords):
...    print "event occured"
...
>>> example = ExampleClass()
>>> example.event += handler
>>> example.do_something()
event occured

It should be noted, that event doesn't necessarily need to be an object
attribute. :class:`Event` instance is basically just a callable object that
works as a sort of "dispatch demultiplexer".

This usage, however, isn't very C#-like. In C#, events are declared in class
scope and that's why the :class:`Event` class also supports the descriptor
protocol (you can use the same way you use the built-in ``property`` object).

>>> from nmevent import Event
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
...    def __init__(self):
...       self._x = None
...       self._y = None
...
>>> def handler(sender, **keywords):
...    print "x changed"
...
>>> example = ExampleClass()
>>> example.x_changed += handler
>>> example.x = 10 # handler gets called
x changed

=======
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

=======
Changes
=======

v0.1
  Initial release.

v0.1.1
  No changes in source code. Improved documentation and unit tests.

v0.2
  Rewritten most of the code. The :class:`Event` class now works as a 
  descriptor, which eliminated the need for a separate :class:`EventSlot`
  class and simplified usage. Added :class:`CallbackStore` to abstract
  the callback storage. 

v0.2.1
  Rewritten some unit tests and added new ones. Improved documentation
  a little bit.

v0.3
  Fixed a major bug, which caused an unbound event not to be actually
  bound when called with an object instance as the first argument.

  Added the :func:`with_properties` class decorator, which automatically
  decorates a class with "private" attributes for each property and
  automatic getters and setters where either one of them is missing.

v0.3.1
  Added docstring tests and fixed all the docstrings so that they
  would pass. As a result, another problem was found with the event
  binding. That problem was fixed by adding the :meth:`InstanceEvent.bind`
  method to be used mainly by the :class:`Property` class when raising
  the "changed" events.
"""

__version__ = __doc__.splitlines()[0].split(' ')[1][1:]
__author__ = u"Jan Milik <milikjan@fit.cvut.cz>"
__all__    = [
    'nmproperty',
    'with_events',
    'with_properties',
    'Event',
]

import __builtin__

EVENTS_ATTRIBUTE = '__nmevents__'

class CallbackStore(object):
    """Collection of callbacks."""

    def __init__(self):
        """Constructor."""
        self.callbacks = set()

    def __iter__(self):
        """Returns the collection's iterator object."""
        return iter(self.callbacks)

    def add(self, callback):
        """Adds a callback to callection.

        :param callback: callable object to be added
        """
        self.callbacks.add(callback)
        return self
    __iadd__ = add

    def remove(self, callback):
        """Removes a callback from the collection.

        :param callback: callback to be removed
        """
        self.callbacks.remove(callback)
        return self
    __isub__ = remove

    def contains(self, callback):
        """Returns ``True`` is ``callback`` is in the collection.

        :param callback: callback to check for
        """
        return callback in self.callbacks
    __contains__ = contains

    def count(self):
        """Returns the number of callbacks in the collection."""
        return len(self.callbacks)
    __len__ = count

    def clear(self):
        """Removes all callbacks from collection."""
        self.callbacks = set()

    def call(self, *args, **keywords):
        """Calls all callbacks with the given arguments."""
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
        """Collection of this event's handlers."""
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
        method, so the last two of the following statements are equivalent:
        
        >>> event.add_handler(handler) # doctest: +SKIP
        >>> event += handler # doctest: +SKIP
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

       >>> isinstance(self.im_sender, self.im_class) # doctest: +SKIP
    """
    
    __slots__ = ('im_event', 'im_class', 'im_sender', )

    @property
    def is_bound(self):
        """``True`` if the event is bound to a sender, ``False`` otherwise."""
        return bool(self.im_sender is not None)

    @property
    def handlers(self):
        """:class:`CallbackStore` object that stores this event's handlers."""
        if not self.is_bound:
            return self.im_event.handlers
        
        sender = self.im_sender
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
                    "%s instance as the first argument." % 
                        (self.im_class.__name__))
            sender = args[0]
            args = args[1:]
            return self.im_event.bind(self.im_class, sender)(*args, **keywords)
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
    
    def bind(self, objtype, obj):
        """Attempts to bind the instance event to an instance.

        Note that this method silently fails and returns self
        when the event is already bound. This is by design
        and is meant to unify the :class:`Event`'s and 
        :class:`InstanceEvent`'s protocol.
        """
        
        if self.is_bound:
            return self
        return InstanceEvent(self.im_event, self.im_class, obj)

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
    ...    @nmevent.nmproperty
    ...    def x(self):
    ...       return self._x
    ...    
    ...    @x.setter
    ...    def x(self, value):
    ...       self._x = value
    ...    
    ...    x_changed = nmevent.Event()
    ...    x.changed = x_changed
    ...    
    ...    def __init__(self):
    ...       self._x = 0
    ...
    >>> def handler(sender, **keywords):
    ...    print "x changed, old value: %r, new value: %r" % (keywords['old_value'], sender.x)
    ...
    >>> example = Example()
    >>> example.x_changed += handler
    >>> example.x = 42
    x changed, old value: 0, new value: 42

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
            self.fire_changed(obj.__class__, obj, old_value)
    
    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError, "Can't delete attribute."
        self.fdel(obj)
    
    def fire_changed(self, objtype, obj, old_value):
        changed = self.changed and self.changed.bind(objtype, obj)
        if changed:
            changed(old_value = old_value)
        property_changed = self.property_changed and self.property_changed.bind(objtype, obj)
        if self.property_changed:
            property_changed(old_value = old_value, name = self.name)
    
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
        """Method decorator to set the delete function.

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
    ...    def x(self, value):
    ...       self._x = value
    ...
    ...    x_changed = nmevent.Event()
    ...    x.changed = x_changed
    ...
    ...    def __init__(self):
    ...       self._x = None
    ...
    >>> def handler(sender, **keywords):
    ...    print "handler called"
    ...
    >>> example = ExampleClass()
    >>> example.x_changed += handler # "handler" will be called when the value of x changes
    >>> example.x = 10 # value of x changed, "handler" gets called
    handler called
    
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
    ...       self._x = value
    ...
    ...    def __init__(self):
    ...       self._x = 0
    ...
    >>> def x_changed_handler(sender, **keywords):
    ...    old_value = keywords['old_value']
    ...    print "x changed; %r -> %r" % (old_value, sender.x)
    ...
    >>> def property_changed_handler(sender, **keywords):
    ...    old_value = keywords['old_value']
    ...    name = keywords['name']
    ...    print "property '%s' changed, %r -> %r" % (name, old_value, sender.x)
    ...
    >>> example = Example()
    >>> example.x_changed += x_changed_handler
    >>> example.property_changed += property_changed_handler
    >>> example.x = 42
    x changed; 0 -> 42
    property 'x' changed, 0 -> 42
    
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
        changed_attr = "%s_changed" % name
        if isinstance(attr, __builtin__.property):
            setattr(clss, changed_attr, Event())
        elif isinstance(attr, Property):
            setattr(clss, changed_attr, Event())
            # Use getattr to bind the event to the class.
            attr.changed = getattr(clss, changed_attr)
            attr.property_changed = property_changed
    return clss

def with_properties(clss):
    """Decorates a class with automatic "private" attributes.
    
    :param clss: class object to decorate.
    :returns:    decorated class
    
    For every :class:`Property` instance within the class'
    dictionary, it creates a setter and getter (unless they
    are already set to a non-None value). These setters
    and getters use "private" attributes - attributes
    that the same name as the property prepended with an
    underscore. In other words, for a property ``foo``,
    you get an attribute called ``_foo`` where the actual
    value is stored.
    
    Usage:
    
    >>> @nmevent.with_properties
    ... class Example(object):
    ...     foo = nmevent.Property()
    ...     foo_changed = nmevent.Event()
    ...     foo.changed = foo_changed
    ...
    >>> def on_foo_changed(sender, old_value):
    ...     print "foo changed"
    ... 
    >>> x = Example()
    >>> x.foo_changed += on_foo_changed
    >>> x.foo = 42 # on_foo_changed gets called
    foo changed
    
    Used together with ``with_events``:
    
    >>> @nmevent.with_events
    ... @nmevent.with_properties
    ... class NextExample(object):
    ...     bar = nmevent.Property()
    ...
    """
    
    def make_getter(attr):
        def getter(self):
            if not hasattr(self, attr):
                setattr(self, attr, None)
            return getattr(self, attr)
        return getter

    def make_setter(attr):
        def setter(self, value):
            setattr(self, attr, value)
        return setter
    
    for name, attr in clss.__dict__.items():
        if isinstance(attr, Property):
            private_attr = "_%s" % name
            if not attr.fget:
                attr.fget = make_getter(private_attr)
            if not attr.fset:
                attr.fset = make_setter(private_attr)
    return clss

def decorated(clss):
    """Convenience decorator, which simply combines the :func:`with_events`
    and :func:`with_properties` decorators.
    """
    return with_events(with_properties(clss))

