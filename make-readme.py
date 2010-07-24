# -*- coding: utf8 -*-

import sys
sys.path.append(sys.path[0] + '/nmevent')

import nmevent

if __name__ == '__main__':
	readme = open('README', 'w')
	readme.write(nmevent.__doc__)

