# https://packaging.python.org/en/latest/distributing.html
# https://github.com/pypa/sampleproject

from setuptools import setup, find_packages
from codecs import open
from os import path, system

import sys, re

here = path.abspath(path.dirname(__file__))

# load __version__, __doc__, _author, _license and _url
exec(open(path.join(here, 'selectq', '__init__.py')).read())

long_description = __doc__

# the following are the required dependencies
# without them, we cannot run byexample
required_deps=[
    'lxml',
    'selenium',
    'requests'
    ]

setup(
    name='selectq',
    version=__version__,

    description=__doc__,
    long_description=long_description,

    url=_url,

    # Author details
    author=_author,
    author_email='use-github-issues@example.com',

    license=_license,

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: Markup :: XML',
        'Topic :: Text Processing :: Markup :: HTML',

        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],

    python_requires='>=3.5',
    install_requires=required_deps,

    keywords='xml xpath, html',

    packages=find_packages(),
    data_files=[("", ["LICENSE"])],
    package_data={'selectq':["gadgets/*"]}
)

