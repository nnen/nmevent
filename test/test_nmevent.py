# -*- coding: utf8 -*-

import sys
sys.path.append(sys.path[0] + '/../nmevent')

import unittest
from nmevent import *

def function_observer_a(sender, *args, **keywords):
	pass

def function_observer_b(sender, *args, **keywords):
	pass

def function_bad_observer():
	pass

class Subject(object):
	def __init__(self):
		self.event_a = Event()
		self.event_b = Event()

	def fire_a(self):
		self.event_a(self)

	def fire_b(self):
		self.event_b(self)

class SlotSubject(object):
	event_a = EventSlot()
	event_b = EventSlot()

	def fire_a(self):
		self.event_a(self)

	def fire_b(self):
		self.event_b(self)

class Observer(object):
	def __init__(self):
		self.event_caught = False
		self.event_count = 0

	def handler(self, sender):
		self.event_caught = True
		self.event_count += 1

class CallableObserver(object):
	def __init__(self):
		self.event_caught = False
		self.event_count = 0

	def __call__(self, *args, **keywords):
		self.event_caught = True
		self.event_count += 1

class EventTest(unittest.TestCase):
	def test_interface(self):
		event = Event()
		observer = Observer()
		try:
			event += observer.handler
			event(self)
			event -= observer.handler
			if observer.handler in event:
				pass
		except:
			self.fail("One of the event operations threw exception.")

	def test_adding(self):
		event = Event()
		observers = [Observer(), Observer(), Observer()]
		
		for observer in observers:
			self.assertFalse(observer in event)

		event += observers[0].handler
		self.assertTrue(observers[0].handler in event)
		self.assertFalse(observers[1].handler in event)
		self.assertFalse(observers[2].handler in event)

		event += observers[1].handler
		self.assertTrue(observers[0].handler in event)
		self.assertTrue(observers[1].handler in event)
		self.assertFalse(observers[2].handler in event)

		event += observers[2].handler
		self.assertTrue(observers[0].handler in event)
		self.assertTrue(observers[1].handler in event)
		self.assertTrue(observers[2].handler in event)

	def test_removing(self):
		event = Event()
		observers = [Observer(), Observer(), Observer()]
		for observer in observers:
			self.assertFalse(observer.handler in observers)
		for observer in observers:
			event += observer.handler
		for observer in observers:
			self.assertTrue(observer.handler in event)
		for observer in observers:
			event -= observer.handler
			self.assertFalse(observer.handler in event)

	def test_fire(self):
		event = Event()
		observers = [Observer(), Observer(), Observer()]

		event(self)
		for observer in observers:
			self.assertEqual(observer.event_count, 0)

		event += observers[0].handler
		event(self)
		self.assertEqual(observers[0].event_count, 1)
		self.assertEqual(observers[1].event_count, 0)
		self.assertEqual(observers[2].event_count, 0)

		event += observers[1].handler
		event(self)
		self.assertEqual(observers[0].event_count, 2)
		self.assertEqual(observers[1].event_count, 1)
		self.assertEqual(observers[2].event_count, 0)

		event -= observers[0].handler
		event(self)
		self.assertEqual(observers[0].event_count, 2)
		self.assertEqual(observers[1].event_count, 2)
		self.assertEqual(observers[2].event_count, 0)

class BoundEventTest(unittest.TestCase):
	def test_fire(self):
		event = BoundEvent(self, Event())
		observer = Observer()
		
		try:
			event += observer.handler
			event()
		except:
			self.fail("BoundEvent threw exception.")
		
		self.assertEqual(observer.event_count, 1)

class WithEventsTest(unittest.TestCase):
	def test_class(self):
		@with_events
		class C(object):
			@property
			def x(self):
				return self._x

			@property
			def y(self):
				return self._y

			def foo(self):
				pass

		self.assertTrue(hasattr(C, 'x_changed'))
		self.assertTrue(hasattr(C, 'y_changed'))
		self.assertTrue(isinstance(C.x_changed, EventSlot))
		self.assertTrue(isinstance(C.y_changed, EventSlot))

		self.assertFalse(hasattr(C, 'foo_changed'))

	def test_instance(self):
		@with_events
		class C(object):
			@property
			def x(self):
				return None

			@x.setter
			def x(self, value):
				self.x_changed()

		c = C()
		
		self.assertTrue(hasattr(c, 'x_changed'))
		self.assertTrue(isinstance(c.x_changed, BoundEvent))

		observer = Observer()
		c.x_changed += observer.handler
		c.x = 10

		self.assertTrue(observer.event_count == 1)

if __name__ == "__main__":
	unittest.main()

