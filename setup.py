#!/usr/bin/env python

from distutils.core import setup

__version__ = "0.0.1-dev1"

LONG_DESCRIPTION = '''
Pysswords encrypt your login credentials in a local file using the scrypt encryption.
'''

setup(
    name='pysswords',
    version=__version__,
    license='License :: OSI Approved :: MIT License',
    description=LONG_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
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
