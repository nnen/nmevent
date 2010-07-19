# -*- coding: utf8 -*-

import unittest
from nmevent import *

class Subject(object):
	def __init__(self):
		self.event_a = Event()
		self.event_b = Event()

	def fire_a(self):
		self.event_a(self)

	def fire_b(self):
		self.event_b(self)

class Observer(object):
	def __init__(self):
		self.event_caught = False

	def handler(self, sender):
		self.event_caught = True

class Test(unittest.TestCase):
	def test_no_handler(self):
		subject = Subject()
		try:
			subject.fire_a()
		except:
			self.fail("Event with no handler threw exception.")

	def test_handling(self):
		subject = Subject()
		observers = [Observer(), Observer(), Observer()]
		for observer in observers:
			subject.event_a += observer.handler
		subject.fire_a()
		for observer in observers:
			self.assertTrue(observer.event_caught)

	def test_removing(self):
		subject = Subject()
		observer_a = Observer()
		observer_b = Observer()

		subject.event_a += observer_a.handler
		subject.event_a += observer_b.handler
		subject.event_a -= observer_b.handler

		subject.fire_a()

		self.assertTrue(observer_a.event_caught)
		self.assertFalse(observer_b.event_caught)
			
if __name__ == "__main__":
	unittest.main()

