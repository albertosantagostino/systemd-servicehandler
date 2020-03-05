#!/usr/bin/env python3

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
]

setup(
    name='servicehandler',
    version='0.9.0',
    author='Alberto Santagostino',
    description='Systemd service/daemon handler',
    license='MIT',
    keywords='Systemd Service Daemon Handler Linux Unix',
    url='https://github.com/albertosantagostino/systemd-servicehandler',
    packages=find_packages(exclude=['tests*']),
    classifiers=classifiers,
    python_requires='>=3.6',
)
