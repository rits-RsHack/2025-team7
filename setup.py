# setup.py

from setuptools import setup, Extension, find_packages
import sys

c_scanner = Extension(
    'c_scanner',
    sources=['src/c_scanner.c']
)

setup(
    name='reaper',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'reaper = src.main:main',
        ],
    },
)