# -*- coding: utf8 -*-

# from distutils.core import setup
from setuptools import setup
import sys

sys.path.append('nmevent')
import nmevent

setup(
	name         = 'nmevent',
	version      = '0.1',
	description  = 'A simple C#-like implementation of the Observer design pattern.',
	long_description = nmevent.__doc__,
	author       = 'Jan Milík',
	author_email = 'milikjan@fit.cvut.cz',

	package_dir  = {'': 'nmevent'},
	py_modules   = ['nmevent'],
	# packages     = ['nmevent', ],
)

