# To run this make file you should have pyenv installed
# https://github.com/yyuu/pyenv
# install pyenv (OSX): `brew install pyenv`
# install pyenv (UBUNTU): `sudo apt-get install pyenv`

PACKAGE=passpie
PACKAGE_TESTS=tests
PY27 = 2.7.9
PY32 = 3.2.6
PY33 = 3.3.6
PY34 = 3.4.2
PYPY = pypy-2.4.0


.PHONY: configure setup-dev test test-py2 test-pypy wheel dist run install-python deploy register check simulate cov clean test-tools

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  setup-dev	=> to install all needed versions of pyenv"
	@echo "  clean		=> to clean clean all automatically generated files"
	@echo "  cov		=> to run coverage"
	@echo "  dist		=> to build $(PACKAGE)"
	@echo "  register	=> to update metadata on pypi servers"
	@echo "  check		=> to check code for smells"
	@echo "  tox		=> to run all tests using tox"
	@echo "  test		=> to run all tests on python $(PY34)"
	@echo "  test-py2	=> to run all tests on python $(PY27)"
	@echo "  test-pypy	=> to run all tests on python $(PYPY)"
	@echo "  simulate	=> to simulate CI tests tasks"
	@echo "  deploy		=> to push binary wheels to pypi servers"

configure: scripts test-tools

install:
	pip install --editable .

test-tools:
	pip install ipython pudb flake8 pytest pytest-cov

setup-dev:
	pyenv install $(PY27) --skip-existing --verbose
	pyenv install $(PY32) --skip-existing --verbose
	pyenv install $(PY33) --skip-existing --verbose
	pyenv install $(PY34) --skip-existing --verbose
	pyenv install $(PYPY) --skip-existing --verbose

clean:
	find $(PACKAGE) -name \*.pyc -delete
	find $(PACKAGE) -name \*__pycache__ -delete
	find $(PACKAGE_TESTS) -name \*.pyc -delete
	find $(PACKAGE_TESTS) -name \*__pycache__ -delete
	python setup.py clean --all
	rm MANIFEST || true
	rm -rf build-* || true
	rm -rf *egg* || true
	rm -rf dist || true
	rm -rf __pycache__ || true

cov:
	py.test --cov .

dist:
	pip install wheel
	python setup.py -q sdist
	python setup.py -q bdist_egg
	python setup.py -q bdist_wheel

	@echo
	@echo "Build files [dist]:"
	@echo "--------------------------"
	@ls -l ./dist/

register:
	pip install pypandoc
	python setup.py register

check:
	flake8
	grep -inr "set_trace()" --color=auto $(PACKAGE) || true
	grep -inr "set_trace()" --color=auto $(PACKAGE_TESTS) || true

test-py2:
	PYENV_VERSION=$(PY27) python -W ignore setup.py -q test

test-pypy:
	PYENV_VERSION=$(PYPY) python -W ignore setup.py -q test

test:
	python -W ignore setup.py -q test

simulate: test test-py2 test-pypy

publish:
	python setup.py publish

tag:
	python setup.py tag

bump-patch:
	bumpversion patch setup.py passpie/cli.py

bump-minor:
	bumpversion minor setup.py passpie/cli.py

deploy-patch: simulate bump-patch register publish tag

deploy-minor: simulate bump-minor register publish tag

deploy: deploy-patch
