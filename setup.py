from setuptools import setup

setup(
    name='questionnaire',
    version='0.3.0',
    description='Uses https://github.com/wong2/pick to prompt user to fill' \
                ' out a questionnaire, and returns the results as a dict',
    keywords='terminal gui pick',
    url='https://github.com/kylebebak/questionnaire',
    download_url = 'https://github.com/kylebebak/questionnaire/tarball/0.3.0',
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
