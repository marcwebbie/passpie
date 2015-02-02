# To run this make file you should have pyenv installed
# https://github.com/yyuu/pyenv
# install pyenv (OSX): `brew install pyenv`
# install pyenv (UBUNTU): `sudo apt-get install pyenv`

PACKAGE=pysswords

PY27 = 2.7.9
PY32 = 3.2.6
PY33 = 3.3.6
PY34 = 3.4.2
PYPY = pypy-2.4.0


set-python:
	pyenv local $(PY27) $(PY32) $(PY33) $(PY34) $(PYPY)
	pyenv rehash

install-python:
	- pyenv virtualenv $(PY27)
	- pyenv virtualenv $(PY32)
	- pyenv virtualenv $(PY33)
	- pyenv virtualenv $(PY34)
	- pyenv virtualenv $(PYPY)


setup: install-python

clean:
	find pysswords -name \*.pyc -delete
	find pysswords -name \*__pycache__ -delete
	python setup.py clean --all
	rm MANIFEST || true
	rm -rf build-*
	rm -rf *egg*
	rm -rf dist

coverage:
	coverage run --source=$(PACKAGE) --omit=$(PACKAGE)/python_two.py setup.py test
	coverage report -m

dist:
	python setup.py -q sdist
	python setup.py -q bdist_egg
	python setup.py -q bdist_wheel

	@echo
	@echo "Build files [dist]:"
	@echo "--------------------------"
	@ls -l ./dist/

run:
	$(eval $(pyenv virtualenv-init -))
	zsh -c "pyenv activate /tmp/my-virtual-env-2.7.9"
	pyenv deactivate

deploy:
	python setup.py sdist bdist_wheel upload -r pypi

tox: set-python
	tox

test:
	python -W ignore setup.py -q test

test-benchmark:
	BENCHMARK=True python -W ignore setup.py -q test

test-all: tox

all: set-python test-all

.PHONY: clean coverage setup test wheel dist run install-python all
