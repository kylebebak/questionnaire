from setuptools import setup

setup(
    name='questionnaire',
    version='1.1.0',
    description='Prompts a user to answer a series of questions. At the end of'\
                ' the questionnaire it returns the answers as a `key -> answer`'\
                ' OrderedDict',
    long_description='Check it out on GitHub...',
    keywords='terminal gui pick question',
    url='https://github.com/kylebebak/questionnaire',
    download_url = 'https://github.com/kylebebak/questionnaire/tarball/1.1.0',
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
