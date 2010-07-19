egg:
	python setup.py bdist_egg

clean:
	rm -fR build dist nmevent.egg-info

unittest:
	./test.sh
