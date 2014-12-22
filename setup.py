#!/usr/bin/env python

from setuptools import setup


__version__ = "0.0.5-dev2"

requirements = [pkg.strip() for pkg in open('requirements.txt').readlines()]

with open("README.rst") as f:
    long_description = f.read() + '\n'

setup(
    name='pysswords',
    version=__version__,
    license='License :: OSI Approved :: MIT License',
    description="Manage your login credentials from the terminal painlessly.",
    long_description=long_description,
    author='Marc Webbie',
    author_email='marcwebbie@gmail.com',
    url='https://github.com/marcwebbie/pysswords',
    scripts=["bin/pysswords"],
    download_url='https://pypi.python.org/pypi/pysswords',
    packages=['pysswords'],
    install_requires=requirements,
    test_suite='tests.test',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Security :: Cryptography',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
