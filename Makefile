PACKAGE=passpie
PACKAGE_TESTS=tests


all: clean develop lint coverage preview

test:
	python -W ignore setup.py -q test

integration-test: install
	bash -x tests/cli.bash

install:
	pip install -U --editable .

develop:
	pip install -U -r requirements/test.txt
	pip install -U -r requirements/release.txt

clean:
	find $(PACKAGE) -name \*.pyc -delete
	find $(PACKAGE) -name \*__pycache__ -delete
	find $(PACKAGE_TESTS) -name \*.pyc -delete
	find $(PACKAGE_TESTS) -name \*__pycache__ -delete
	python setup.py clean -q --all
	rm -rf MANIFEST || true
	rm -rf build-* || true
	rm -rf *egg* || true
	rm -rf dist || true
	rm -rf __pycache__ || true

coverage:
	python setup.py coverage

docs:
	$(MAKE) -C docs/ clean
	$(MAKE) -C docs/ html
	cd docs/_build/html && python3 -m http.server

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

lint:
	flake8
	grep -inr "set_trace()" --color=auto $(PACKAGE) || true
	grep -inr "set_trace()" --color=auto $(PACKAGE_TESTS) || true

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

preview:
	@echo "Commits not included in last version"
	@echo "======================"
	git log `git describe --tags --abbrev=0`..HEAD --oneline

release-patch: lint test bump-patch register publish tag

release-minor: lint test bump-minor register publish tag

release-major: lint test bump-major register publish tag

.PHONY: docs
