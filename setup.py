"""

pdfgen :  Copyright 2018, Blake Huber

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

see: https://www.apache.org/licenses/LICENSE-2.0

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
contained in the program LICENSE file.

"""

import os
import sys
from setuptools import setup, find_packages
from codecs import open
import pdfgen


requires = [
    'Jinja2',
    'pdfkit',
    'MarkupSafe',
    'PyYAML',
    'Pygments',
    'pytz',
    'xmltodict'
]


def read(fname):
    basedir = os.path.dirname(sys.argv[0])
    return open(os.path.join(basedir, fname)).read()


setup(
    name='pdfgen',
    version=pdfgen.__version__,
    description='PDF Document Generation',
    long_description=read('DESCRIPTION.rst'),
    url='https://github.com/fstab50/pdfgen',
    author=pdfgen.__author__,
    author_email=pdfgen.__email__,
    license='Apache',
    classifiers=[
        'Topic :: Documentation',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows'
    ],
    keywords='pdf document generation reports xml json wkhtmltopdf',
    packages=find_packages(exclude=['docs', 'scripts', 'assets']),
    install_requires=requires,
    python_requires='>=3.4, <4',
    entry_points={
        'console_scripts': [
            'pdfgen=pdfgen.cli:init_cli',
            'pdfconfig=pdfgen.cli:option_configure'
        ]
    },
    zip_safe=False
)
