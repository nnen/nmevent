# -*- coding: utf8 -*-

import sys
sys.path.append(sys.path[0] + '/../nmevent')

import unittest
import nmevent

def function_observer_a(sender, *args, **keywords):
	pass

def function_observer_b(sender, *args, **keywords):
	pass

def function_bad_observer():
	pass

class Subject(object):
	def __init__(self):
		self.event_a = nmevent.Event()
		self.event_b = nmevent.Event()

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

class CallbackStoreTest(unittest.TestCase):
	def test_interface(self):
		store = nmevent.CallbackStore()
		observer = Observer()

		try:
			store += observer.handler
		except TypeError:
			self.fail("The \"+=\" operator is not supported.")

		try:
			store -= observer.handler
		except TypeError:
			self.fail("The \"-=\" operator is not supported.")

		try:
			observer.handler in store
		except TypeError:
			self.fail("The \"in\" operator is not supported.")

		try:
			for callback in store:
				pass
		except TypeError:
			self.fail("Iteration is not supported.")

		try:
			len(store)
		except TypeError:
			self.fail("\"len\" operator is not supported.")
	
	def test_adding(self):
		observers = [Observer(), Observer(), Observer(), ]
		store = nmevent.CallbackStore()

		self.assertEqual(len(store), 0)
		self.assertEqual(store.count(), 0)
		store += observers[0]
		self.assertEqual(len(store), 1)
		self.assertEqual(store.count(), 1)
		store += observers[0]
		self.assertEqual(len(store), 1)
		self.assertEqual(store.count(), 1)
		store += observers[1]
		self.assertEqual(len(store), 2)
		self.assertEqual(store.count(), 2)
		store += observers[2]
		self.assertEqual(len(store), 3)
		self.assertEqual(store.count(), 3)

		store = nmevent.CallbackStore()
		for x in range(100):
			observer = Observer()
			self.assertFalse(observer.handler in store)
			self.assertFalse(store.contains(observer.handler))
			store += observer.handler
			self.assertTrue(observer.handler in store)
			self.assertTrue(store.contains(observer.handler))
			self.assertEqual(len(store), x + 1)
			self.assertEqual(store.count(), x + 1)
	
	def test_removing(self):
		observers = [Observer(), Observer(), Observer(), ]
		store = nmevent.CallbackStore()

		for observer in observers:
			store += observer.handler
		for observer in observers:
			self.assertTrue(observer.handler in store)

		store -= observers[0].handler
		self.assertFalse(observers[0].handler in store)
		self.assertTrue(observers[1].handler in store)
		self.assertTrue(observers[2].handler in store)

		store -= observers[1].handler
		self.assertFalse(observers[0].handler in store)
		self.assertFalse(observers[1].handler in store)
		self.assertTrue(observers[2].handler in store)

		store -= observers[2].handler
		self.assertFalse(observers[0].handler in store)
		self.assertFalse(observers[1].handler in store)
		self.assertFalse(observers[2].handler in store)

		self.assertEqual(len(store), 0)
		self.assertEqual(store.count(), 0)
	
	def test_clearing(self):
		store = nmevent.CallbackStore()

		for x in range(100):
			observer = Observer()
			store += observer.handler

		self.assertEqual(len(store), 100)
		self.assertEqual(store.count(), 100)

		store.clear()

		self.assertEqual(len(store), 0)
		self.assertEqual(store.count(), 0)

		observer = Observer()

		store += observer.handler

		self.assertNotEqual(len(store), 0)
		self.assertNotEqual(store.count(), 0)
		self.assertTrue(observer.handler in store)

		store.clear()

		self.assertEqual(len(store), 0)
		self.assertEqual(store.count(), 0)
		self.assertFalse(observer.handler in store)
	
class EventTest(unittest.TestCase):
	def test_interface(self):
		event = nmevent.Event()
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
		event = nmevent.Event()
		observers = [Observer(), Observer(), Observer()]
		
		for observer in observers:
			self.assertFalse(observer.handler in event)

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
		event = nmevent.Event()
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
		event = nmevent.Event()
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
	
	def test_descriptor(self):
		event1 = nmevent.Event()
		event2 = nmevent.Event()
		class TestClass(object):
			pass
		TestClass.event1 = event1
		TestClass.event2 = event2
		test1 = TestClass()
		test2 = TestClass()
		self.assertFalse(event1 is TestClass.event1)
		self.assertFalse(TestClass.event1 is test1.event1)
		self.assertFalse(test1.event1 is test2.event1)
		self.assertFalse(test1.event1 is test1.event2)
		self.assertFalse(test1.event1.im_event is test1.event2.im_event)

		self.assertTrue(isinstance(test1.event1, nmevent.InstanceEvent))

		observer1 = Observer()
		observer2 = Observer()

		test1.event1 += observer1.handler
		test1.event2 += observer2.handler
		test1.event1()
		self.assertEqual(observer1.event_count, 1)
		self.assertEqual(observer2.event_count, 0)
		test2.event1()
		self.assertEqual(observer1.event_count, 1)
		self.assertEqual(observer2.event_count, 0)
		test1.event2()
		self.assertEqual(observer1.event_count, 1)
		self.assertEqual(observer2.event_count, 1)
	
	def test_descriptor_get(self):
		class TestClass(object):
			event = nmevent.Event()
		self.assertTrue(isinstance(TestClass.__dict__['event'], nmevent.Event))
		self.assertTrue(isinstance(TestClass.event, nmevent.InstanceEvent))
		self.assertFalse(TestClass.event.is_bound)

		test1 = TestClass()
		test2 = TestClass()
		self.assertTrue(isinstance(test1.event, nmevent.InstanceEvent))
		self.assertTrue(test1.event.is_bound)
		self.assertFalse(test1.event is test2.event)
		self.assertTrue(test1.event.im_event is test2.event.im_event)
		self.assertTrue(test1.event.handlers is test1.event.handlers)
		self.assertFalse(test1.event.handlers is test2.event.handlers)
	
	def test_descriptor_set(self):
		event = nmevent.Event()
		class TestClass(object):
			pass
		TestClass.event = event
		def test():
			TestClass.event = "any value"
		#self.assertRaises(AttributeError, test)
		self.assertTrue(TestClass.__dict__['event'] is event)
	
	def test_descriptor_delete(self):
		class TestClass(object):
			event = nmevent.Event()
		inst = TestClass()
		def test():
			del inst.event
		self.assertRaises(AttributeError, test)
		self.assertTrue(isinstance(inst.event, nmevent.InstanceEvent))

class TestInstanceEvent(unittest.TestCase):
	def setUp(self):
		self.event = nmevent.Event()
		class TestClass(object):
			pass
		self.test_class = TestClass
		self.instance = TestClass()
		self.unbound = nmevent.InstanceEvent(self.event, TestClass)
		self.bound = nmevent.InstanceEvent(self.event, TestClass, self.instance)
	
	def test_call_unbound(self):
		def test():
			self.unbound()
		self.assertRaises(TypeError, test)

		try:
			self.unbound(self.instance)
		except TypeError:
			self.fail("Cannot call unbound event with instance.")

		def test():
			self.unbound("not a TestClass")
		self.assertRaises(TypeError, test)

	def test_call_bound(self):
		try:
			self.bound()
		except TypeError:
			self.fail("Cannot call bound event without instance.")
	
class PropertyTest(unittest.TestCase):
	def setUp(self):
		class TestClass(object):
			def get_x(self):
				return self._x
			def set_x(self, value):
				self._x = value
			def __init__(self):
				self._x = None
			x = nmevent.Property(get_x, set_x)
			no_rw = nmevent.Property()
		self.test_class = TestClass
		self.instance = TestClass()
	
	def test_get_set(self):
		try:
			self.instance.x = 13
		except AttributeError:
			self.fail("Setter threw error.")

		self.assertEqual(self.instance.x, 13)

		def test():
			self.instance.no_rw = 13
		self.assertRaises(AttributeError, test)

class WithEventsTest(unittest.TestCase):
	def test_class(self):
		@nmevent.with_events
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
		self.assertTrue(isinstance(C.x_changed, nmevent.InstanceEvent))
		self.assertTrue(isinstance(C.y_changed, nmevent.InstanceEvent))

		self.assertFalse(hasattr(C, 'foo_changed'))

	def test_instance(self):
		@nmevent.with_events
		class C(object):
			@property
			def x(self):
				return None

			@x.setter
			def x(self, value):
				self.x_changed()

		c = C()
		
		self.assertTrue(hasattr(c, 'x_changed'))
		self.assertTrue(isinstance(c.x_changed, nmevent.InstanceEvent))

		observer = Observer()
		c.x_changed += observer.handler
		c.x = 10

		self.assertTrue(observer.event_count == 1)

def do_test():
	unittest.main()

if __name__ == "__main__":
	do_test()

