#!/usr/bin/env python

import io
import os
import sys

try:
    from setuptools import setup, Command, find_packages
except ImportError:
    from distutils.core import setup, Command, find_packages


__version__ = "1.5.5"

with io.open('README.rst', encoding='utf-8') as readme_file:
    long_description = readme_file.read() + "\n\n"

if sys.argv[-1] == 'tag':
    os.system("git tag -a v%s -m 'version v%s'" % (__version__, __version__))
    os.system("git push --tags")
    os.system("git push")
    sys.exit()


requirements = [
    'click==6.6',
    'PyYAML==3.11',
    'tabulate==0.7.5',
    'tinydb==3.2.1',
    'rstr==2.2.4',
]


class PyTest(Command):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        self.pytest_args = ["-v", "tests/"]

    def finalize_options(self):
        pass

    def run(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


class PyTestCoverage(PyTest):

    def initialize_options(self):
        self.pytest_args = [
            "-v", "tests",
            "--cov", 'passpie',
            "--cov-config", ".coveragerc",
            "--cov-report", "term-missing",
        ]


setup(
    name='passpie',
    version=__version__,
    license='License :: OSI Approved :: MIT License',
    description="Manage your login credentials from the terminal painlessly.",
    long_description=long_description,
    author='Marcwebbie',
    author_email='marcwebbie@gmail.com',
    url='https://github.com/marcwebbie/passpie',
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
