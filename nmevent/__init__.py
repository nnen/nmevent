# -*- encoding: utf-8 -*-
"""
Copyright (c) 2010, Jan Milík.
"""

__author__ = u"Jan Milík"
__all__    = ['Event', 'EventArgs']

class Event(object):
	def __init__(self):
		self.handlers = set()
	
	def addHandler(self, handler):
		self.handlers.add(handler)
		return self
	__iadd__ = addHandler
	
	def removeHandler(self, handler):
		self.handlers.remove(handler)
		return self
	__isub__ = removeHandler
	
	def fire(self, sender, *args, **keywords):
		for handler in self.handlers:
			handler(sender, *args, **keywords)
	__call__ = fire
	
	def disconnect(self):
		self.handlers = set()

class EventArgs(object):
	pass

