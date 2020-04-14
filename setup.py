"""
Module setup for the 'pyaw-reporting' package.

See:
https://github.com/gmontamat/pyaw-reporting
"""

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

setup(
    name='pyaw-reporting',
    version='0.0.5',
    description='AdWords API Reporting in Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/gmontamat/pyaw-reporting',
    author='Gustavo Montamat',
    # author_email='',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='adwords adwords-api adwords-reports googleads awql',
    packages=find_packages(),
    install_requires=['googleads'],
    entry_points={
        'console_scripts': [
            'awreporting=awreporting.command_line:main'
        ]
    },
)
