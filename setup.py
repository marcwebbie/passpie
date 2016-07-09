#!/usr/bin/env python

import io
import os
import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages


__version__ = "2.0"

with io.open('README.rst', encoding='utf-8') as readme_file:
    long_description = readme_file.read() + "\n\n"


if sys.argv[-1] == 'tag':
    os.system("git tag -a v%s -m 'version v%s'" % (__version__, __version__))
    sys.exit()


requirements = [
    'click==6.6',
    'PyYAML==3.11',
    'tabulate==0.7.5',
    'tinydb==3.2.1',
    'rstr==2.2.4',
    "pyperclip==1.5.27",
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
    test_suite='tests',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
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
        'Topic :: System :: Systems Administration',
    ],
)
