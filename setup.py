from __future__ import unicode_literals

import io
import os
from setuptools import setup

import tyrian

here = os.path.abspath(os.path.dirname(__file__))


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.md')


setup(
    name='tyrian',
    version=tyrian.__version__,
    url='http://github.com/Mause/tyrian/',
    license='Apache Software License',
    author='Dominic May',
    # tests_require=['pytest'],
    install_requires=[],
    # cmdclass={'test': PyTest},
    author_email='me@mause.me',
    # description='Automated REST APIs for existing database-driven systems',
    long_description=long_description,
    packages=['tyrian'],
    include_package_data=True,
    platforms='any',
    # test_suite='sandman.test.test_sandman',
    classifiers=[
        'Programming Language :: Python 3',
        # 'Development Status :: 4 - Beta',
        'Natural Language :: English',
        # 'Environment :: Web Environment',
        # 'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        # 'Topic :: Software Development :: Libraries :: Python Modules',
        # 'Topic :: Software Development :: Libraries :: Application Frameworks',
        # 'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
    extras_require={
        # 'testing': ['pytest'],
    }
)