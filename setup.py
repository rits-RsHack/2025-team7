# setup.py

from setuptools import setup, Extension, find_packages
import sys

c_scanner = Extension(
    'c_scanner',
    sources=['src/scanner/c_scanner/scanner.c']
)

setup(    
    name='reaper',
    version='0.2.0',
    packages=find_packages(),

    install_requires=[
        'tqdm',
    ],

    ext_modules=[c_scanner],

    entry_points={
        'console_scripts': [
            'reaper = src.main:main',
        ],
    },
)