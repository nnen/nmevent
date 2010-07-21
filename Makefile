egg:
	python setup.py bdist_egg

wininst:
	python setup.py bdist_wininst

clean:
	rm -fR build dist nmevent.egg-info

unittest:
	python test/test_nmevent.py
