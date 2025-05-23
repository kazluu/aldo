#!/usr/bin/env python3
from setuptools import setup, find_packages
from aldo import __version__

# The setup.py is kept minimal with just enough configuration to handle packaging
setup(
    name="aldo",
    version=__version__,
    packages=find_packages(include=["aldo", "aldo.*"]),
    include_package_data=True,
)