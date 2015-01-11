#!/usr/bin/env python
import os
from setuptools import setup, find_packages

requirements_file = "requirements.txt"
version_file = os.path.join('pysswords', '__version__.py')
requirements = [pkg.strip() for pkg in open(requirements_file).readlines()]
version = open(version_file).read().strip()

with open("README.md") as f:
    long_description = f.read() + '\n'

setup(
    name='pysswords',
    version=version,
    license='License :: OSI Approved :: MIT License',
    description="Manage your login credentials from the terminal painlessly.",
    long_description=long_description,
    author='Marcwebbie',
    author_email='marcwebbie@gmail.com',
    url='https://github.com/marcwebbie/pysswords',
    download_url='https://pypi.python.org/pypi/pysswords',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pysswords = pysswords.__main__:main',
        ]
    },
    install_requires=requirements,
    tests_require=['mock'],
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
