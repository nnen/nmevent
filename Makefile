egg:
	python setup.py bdist_egg

wininst:
	python setup.py bdist_wininst

clean:
	rm -fR build dist nmevent.egg-info htmlcov
	rm -fR nmevent/nmevent.egg-info nmevent/*.pyc
	rm -f .coverage

testonly:
	python test/test_nmevent.py

unittest:
	coverage run test/test_nmevent.py
	echo
	coverage report -m
	coverage html

lint:
	pylint nmevent/nmevent.py

