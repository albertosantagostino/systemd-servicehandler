#!/usr/bin/env python3

# Installer of systemd-servicehandler
# Run 'python3 setup.py install' to install locally the current version
# Run 'python3 setup.py sdist bdist_wheel' to generate distribution archives

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
]

setup(
    name='servicehandler',
    version='0.9',
    author='Alberto Santagostino',
    description='Systemd service handler',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    keywords='Systemd Service Daemon Handler Linux Unix',
    url='https://github.com/albertosantagostino/systemd-servicehandler',
    packages=find_packages(exclude=['tests*']),
    classifiers=classifiers,
    python_requires='>=3.6',
)