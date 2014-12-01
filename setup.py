#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


__version__ = "0.0.4.2"

with open("README.rst") as f:
    long_description = f.read()
    ind = long_description.find("\n")
    long_description = long_description[ind + 1:]

setup(
    name='pysswords',
    version=__version__,
    license='License :: OSI Approved :: MIT License',
    description="Pysswords encrypt your login credentials in a local file using the scrypt encryption.",
    long_description=long_description,
    author='Marc Webbie',
    author_email='marcwebbie@gmail.com',
    url='https://github.com/marcwebbie/pysswords',
    packages=['pysswords'],
    install_requires=open('requirements.txt').readlines(),
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
        'Programming Language :: Python :: 3.3',
    ],
)
