#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup, Command, find_packages
except ImportError:
    from distutils.core import setup, Command, find_packages


__version__ = "1.0"


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()


if sys.argv[-1] == 'tag':
    os.system("git tag -a v%s -m 'version v%s'" % (__version__, __version__))
    os.system("git push --tags")
    sys.exit()

requirements = [
    'click==5.1',
    'PyYAML==3.11',
    'tabulate==0.7.5',
    'tinydb==2.4',
]


long_description = open('README.md').read() + "\n\n"


class PyTest(Command):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        self.pytest_args = []

    def finalize_options(self):
        pass

    def run(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


class PyTestCoverage(PyTest):

    def initialize_options(self):
        self.pytest_args = ['--cov', 'passpie']


setup(
    name='passpie',
    version=__version__,
    license='License :: OSI Approved :: MIT License',
    description="Manage your login credentials from the terminal painlessly.",
    long_description=long_description,
    author='Marcwebbie',
    author_email='marcwebbie@gmail.com',
    url='https://marcwebbie.github.io/passpie',
    download_url='https://github.com/marcwebbie/passpie',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'passpie=passpie.cli:cli',
        ]
    },
    install_requires=requirements,
    cmdclass={'test': PyTest, 'coverage': PyTestCoverage},
    test_suite='tests',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python',
        'Topic :: Security :: Cryptography',
    ],
)
