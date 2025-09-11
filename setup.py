# setup.py

from setuptools import setup, Extension, find_packages
import sys

# OSによって必要なライブラリを切り替える
libraries = []
if sys.platform == 'win32':
    libraries.append('Ws2_32')

c_scanner_module = Extension(
    'c_scanner',
    sources=['src/scanner/c_scanner/scanner.c'],
    libraries=libraries  # 👈 ここにライブラリリストを渡す
)

setup(    
    name='reaper',
    version='0.2.0',
    packages=find_packages(),

    install_requires=[
        'tqdm',
    ],

    ext_modules=[c_scanner_module],

    entry_points={
        'console_scripts': [
            'reaper = src.main:main',
        ],
    },
)