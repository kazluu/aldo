#!/usr/bin/env python3
from setuptools import setup, find_packages

# The setup.py is kept minimal with just enough configuration to handle packaging
setup(
    name="aldo",
    version="1.0.0",
    packages=find_packages(include=["aldo", "aldo.*"]),
    include_package_data=True,
)