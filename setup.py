#!/usr/bin/env python
from setuptools import setup, find_packages


__version__ = "0.1rc2"

requirements_file = "requirements.txt"
requirements = [pkg.strip() for pkg in open(requirements_file).readlines()]
requirements_test_file = "requirements_test.txt"
requirements_tests = [pkg.strip() for pkg in open(requirements_file).readlines()]

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst') + "\n"
except(IOError, ImportError):
    long_description = open('README.md').read() + "\n"

setup(
    name='passpie',
    version=__version__,
    license='License :: OSI Approved :: MIT License',
    description="Manage your login credentials from the terminal painlessly.",
    long_description=long_description,
    author='Marcwebbie',
    author_email='marcwebbie@gmail.com',
    url='https://github.com/marcwebbie/passpie',
    download_url='https://pypi.python.org/pypi/passpie',
    packages=find_packages(),
    entry_points="""
        [console_scripts]
        passpie=passpie.cli:cli
    """,
    install_requires=requirements,
    tests_require=requirements_tests,
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
