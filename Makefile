.PHONY: build 

ifndef VTENV_OPTS
VTENV_OPTS = "--no-site-packages"
endif

bin/python:
	virtualenv $(VTENV_OPTS) .
	bin/python setup.py develop

test: bin/python
	bin/pip install numpy
	bin/pip install matplotlib
