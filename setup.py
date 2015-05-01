#!/usr/bin/env python
from setuptools import setup, find_packages


__version__ = "0.1beta1"

requirements_file = "requirements.txt"
requirements = [pkg.strip() for pkg in open(requirements_file).readlines()]
requirements_tests = ["mock", "flake8", "coverage"]

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
        'Development Status :: 2 - Beta',
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
