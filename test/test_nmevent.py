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

class Test(unittest.TestCase):
	def test_no_handler(self):
		subject = Subject()
		observer = Observer()
		callable = CallableObserver()
		self.assertFalse(function_observer_a in subject.event_a)
		self.assertFalse(observer.handler in subject.event_a)
		self.assertFalse(callable in subject.event_a)
		try:
			subject.fire_a()
		except:
			self.fail("Event with no handler threw exception.")
		
	def test_function_handlers(self):
		subject = Subject()
		subject.event_a += function_observer_a
		subject.event_a += function_observer_b
		try:
			subject.fire_a()
		except:
			self.fail("Event with function handlers threw exception.")
	
	def test_method_handlers(self):
		subject = Subject()
		observers = [Observer(), Observer(), Observer()]
		for observer in observers:
			subject.event_a += observer.handler
		for observer in observers:
			self.assertTrue(observer.handler in subject.event_a)
		subject.fire_a()
		for observer in observers:
			self.assertTrue(observer.event_count == 1)

	def test_callable_handlers(self):
		subject = Subject()
		observers = [CallableObserver(), CallableObserver(), CallableObserver()]
		for observer in observers:
			subject.event_a += observer
		for observer in observers:
			self.assertTrue(observer in subject.event_a)
		subject.fire_a()
		for observer in observers:
			self.assertTrue(observer.event_count == 1)

	def test_removing(self):
		subject = Subject()
		observer_a = Observer()
		observer_b = Observer()
		observer_c = Observer()

		subject.event_a += observer_a.handler
		subject.event_a += observer_b.handler
		self.assertTrue(observer_a.handler in subject.event_a)
		self.assertTrue(observer_b.handler in subject.event_a)

		subject.fire_a()
		self.assertTrue(observer_a.event_count == 1)
		self.assertTrue(observer_b.event_count == 1)
		self.assertTrue(observer_c.event_count == 0)

		self.assertTrue(observer_b.handler in subject.event_a)
		subject.event_a -= observer_b.handler
		self.assertFalse(observer_b.handler in subject.event_a)

		subject.fire_a()

		self.assertTrue(observer_a.event_count == 2)
		self.assertTrue(observer_b.event_count == 1)
		self.assertTrue(observer_c.event_count == 0)

	def test_exception(self):
		subject = Subject()
		subject.event_a += function_bad_observer
		self.assertRaises(TypeError, subject.fire_a)

	def test_slot(self):
		subject = SlotSubject()
		observer_a = Observer()
		observer_b = Observer()
		subject.event_a += observer_a.handler
		subject.event_b += observer_b.handler
		subject.event_a(subject)

		self.assertTrue(observer_a.event_caught)
		self.assertFalse(observer_b.event_caught)

	def test_slot_static(self):
		self.assertTrue(isinstance(SlotSubject.event_a, EventSlot))

	def test_disconnect(self):
		subject = SlotSubject()
		observers = [Observer(), Observer(), Observer()]
		for observer in observers:
			subject.event_a += observer.handler
		subject.fire_a()
		for observer in observers:
			self.assertTrue(observer.event_count == 1)
		subject.event_a.disconnect()
		subject.fire_a()
		for observer in observers:
			self.assertTrue(observer.event_count == 1)

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
				self.x_changed(self)

		c = C()
		
		self.assertTrue(hasattr(c, 'x_changed'))
		self.assertTrue(isinstance(c.x_changed, Event))

		observer = Observer()
		c.x_changed += observer.handler
		c.x = 10

		self.assertTrue(observer.event_count == 1)

if __name__ == "__main__":
	unittest.main()

