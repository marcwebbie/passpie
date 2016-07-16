PACKAGE=passpie
PACKAGE_TESTS=tests


all: clean develop lint test-all news

#######################
# Installation
#######################
install:
	pip install -U --editable .

release:
	pip install -U -r requirements/release.txt

develop: release install
	pip install -U -r requirements/test.txt

#######################
# Tests
#######################
test:
	py.test -v tests

test-all:
	tox

coverage:
	py.test -v tests --cov passpie --cov-config .coveragerc --cov-report term-missing

lint:
	flake8
	grep -inr "set_trace()" --color=auto $(PACKAGE) || true
	grep -inr "set_trace()" --color=auto $(PACKAGE_TESTS) || true


#######################
# Setup
#######################
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

docs:
	$(MAKE) -C docs/ clean
	$(MAKE) -C docs/ html

serve-docs: docs
	cd docs/_build/html && python3 -m http.server


#######################
# Release
#######################
dist:
	pip install -U pip wheel
	python setup.py -q sdist bdist_wheel

	@echo
	@echo "Build files [dist]:"
	@echo "--------------------------"
	@ls -l ./dist/

register:
	pip install pypandoc
	python setup.py register

publish:
	python setup.py sdist bdist_wheel upload

tag:
	python setup.py tag

formula:
	poet -f passpie > passpie.rb

bump-patch:
	bumpversion patch setup.py passpie/cli.py

bump-minor:
	bumpversion minor setup.py passpie/cli.py

bump-major:
	bumpversion major setup.py passpie/cli.py

news:
	@echo "################################################"
	@echo "Commits not included in last version"
	@echo "################################################"
	@git log `git describe --tags --abbrev=0`..HEAD --pretty=format:"+ **✔** %s"

ensure-news-patch:
	grep 'Version $(shell bumpversion --allow-dirty --dry-run --list patch | grep new_version | sed s,"^.*=",,)' docs/changelog.rst

ensure-news-minor:
	grep 'Version $(shell bumpversion --allow-dirty --dry-run --list minor | grep new_version | sed s,"^.*=",,)' docs/changelog.rst

ensure-news-major:
	grep 'Version $(shell bumpversion --allow-dirty --dry-run --list major | grep new_version | sed s,"^.*=",,)' docs/changelog.rst

release-patch: ensure-news-patch lint test bump-patch dist register publish tag formula

release-minor: ensure-news-minor lint test bump-minor dist register publish tag formula

release-major: ensure-news-major lint test bump-major dist register publish tag formula

.PHONY: docs news
