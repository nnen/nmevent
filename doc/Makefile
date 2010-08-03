
SPHINX-BUILD = sphinx-build

html: conf.py index.rst ../nmevent/nmevent.py
	$(SPHINX-BUILD) . html/

text: text/index.txt

text/index.txt: conf.py index.rst ../nmevent/nmevent.py
	$(SPHINX-BUILD) -b text . text/

clean:
	rm -fR _build/* html text

