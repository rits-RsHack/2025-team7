# setup.py

from setuptools import setup, find_packages

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