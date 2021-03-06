PYTHON = python
PYLINT = pylint
COVERAGE = coverage
SPHINX-BUILD = sphinx-build

sdist: README docs
	$(PYTHON) setup.py sdist

egg: README docs
	$(PYTHON) setup.py bdist_egg

wininst: README docs
	$(PYTHON) setup.py bdist_wininst

upload-linux: README docs
	$(PYTHON) setup.py sdist upload
	$(PYTHON) setup.py bdist_egg upload

upload-win: README docs
	$(PYTHON) setup.py sdist upload
	$(PYTHON) setup.py bdist_egg upload
	$(PYTHON) setup.py bdist_windows upload

docs: doc/conf.py doc/index.rst nmevent/nmevent.py
	make -C doc html

clean:
	rm -fR build dist nmevent.egg-info htmlcov doc/html
	rm -fR nmevent/nmevent.egg-info nmevent/*.pyc
	rm -f .coverage README
	make -C doc clean

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
	rm -f README
	make -C doc text/index.txt
	cp doc/text/index.txt README

