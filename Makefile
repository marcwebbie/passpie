PACKAGE=passpie
PACKAGE_TESTS=tests

all: check coverage

test:
	python -W ignore setup.py -q test

install:
	pip install -U --editable .

develop:
	pip install -U -r requirements_tests.txt

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

coverage:
	py.test --cov passpie --cov-config .coveragerc --cov-report=term-missing

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

simulate: check test

publish:
	python setup.py publish

tag:
	python setup.py tag

bump-patch:
	bumpversion patch setup.py passpie/cli.py

bump-minor:
	bumpversion minor setup.py passpie/cli.py

bump-major:
	bumpversion major setup.py passpie/cli.py

deploy-patch: simulate bump-patch register publish tag

deploy-minor: simulate bump-minor register publish tag

deploy-major: simulate bump-major register publish tag

deploy: deploy-patch
