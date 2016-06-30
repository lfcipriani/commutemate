# The template used for this file is at https://github.com/pypa/sampleproject/blob/master/setup.py
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='commutemate',
    version='0.0.1',
    description='Experimenting with commute data from GPX files to check how I can improve my ride.',
    long_description=long_description,
    url='https://github.com/lfcipriani/commutemate',
    author='Luis Cipriani',
    license='Apache v2',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache v2',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='gpx data geo commute ride',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['gpxpy', 'numpy', 'scipy', 'scikit-learn'],
    extras_require={
        'test': ['nose'],
    },
    entry_points={
        'console_scripts': [
            'commutemate=commutemate.cli:main',
        ],
    },
)
