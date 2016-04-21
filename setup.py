import os
from setuptools import setup

def fread(fname):
    filepath = os.path.join(os.path.dirname(__file__), fname)
    with open(filepath, 'r') as fp:
        return fp.read()

setup(
    name='questionnaire',
    version='0.4.0',
    description='Uses https://github.com/wong2/pick to prompt user to fill' \
                ' out a questionnaire, and returns the results as a dict',
    long_description=fread('README.md'),
    keywords='terminal gui pick',
    url='https://github.com/kylebebak/questionnaire',
    download_url = 'https://github.com/kylebebak/questionnaire/tarball/0.4.0',
    author='kylebebak',
    author_email='kylebebak@gmail.com',
    license='MIT',
    packages=['questionnaire'],
    install_requires=['pick==0.6.0'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ]
)
