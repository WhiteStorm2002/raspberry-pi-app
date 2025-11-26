#!/usr/bin/env python3
"""
Setup-Konfiguration für die Raspberry Pi App
"""

from setuptools import setup, find_packages
import os

# Lese die README-Datei
def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

# Lese die Requirements
def read_requirements():
    filepath = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name='raspberry-pi-app',
    version='1.0.0',
    description='Eine Python-Anwendung für Raspberry Pi',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    author='Leon Haas',
    author_email='haas-leon-2002@gmx.de',
    url='https://github.com/WhiteStorm2002/raspberry-pi-app',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=read_requirements(),
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'raspi-app=app.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: System :: Hardware',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    keywords='raspberry-pi gpio hardware iot',
)

