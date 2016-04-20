#-*-coding:utf-8-*-

import os
from setuptools import setup

def fread(fname):
    filepath = os.path.join(os.path.dirname(__file__), fname)
    with open(filepath, 'r') as fp:
        return fp.read()

setup(
    name='questionnaire',
    version='0.2.0',
    description='uses pick to ',
    long_description=fread('README.md'),
    keywords='terminal gui pick',
    url='https://github.com/kylebebak/questionnaire',
    author='kylebebak',
    author_email='kylebebak@gmail.com',
    license='MIT',
    packages=['questionnaire'],
    tests_require=['nose'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ]
)
