# -*- coding: utf8 -*-

# from distutils.core import setup
from setuptools import setup
import sys

sys.path.append('nmevent')
import nmevent

setup(
	name             = 'nmevent',
	version          = '0.1.1',
	author           = 'Jan Milík',
	author_email     = 'milikjan@fit.cvut.cz',
	description      = 'A simple C#-like implementation of the Observer design pattern.',
	long_description = nmevent.__doc__,
	url              = 'http://pypi.python.org/pypi/nmevent',
	
	package_dir = {'': 'nmevent'},
	py_modules  = ['nmevent'],
	# packages  = ['nmevent', ],
	keywords    = 'library event observer pattern',
	license     = 'Lesser General Public License v3',
	
	classifiers = [
		'Development Status :: 1 - Planning',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
		'Natural Language :: English',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 2.6',
	]
)

