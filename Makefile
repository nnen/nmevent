PYTHON = python
PYLINT = pylint
COVERAGE = coverage

egg: README
	$(PYTHON) setup.py bdist_egg

wininst: README
	$(PYTHON) setup.py bdist_wininst

clean:
	rm -fR build dist nmevent.egg-info htmlcov
	rm -fR nmevent/nmevent.egg-info nmevent/*.pyc
	rm -f .coverage README

testonly:
	$(PYTHON) test/test_nmevent.py

unittest:
	$(COVERAGE) run test/test_nmevent.py
	echo
	$(COVERAGE) report -m
	$(COVERAGE) html

lint:
	$(PYLINT) nmevent/nmevent.py

README: nmevent/nmevent.py
	$(PYTHON) make-readme.py

