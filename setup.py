"""
Setup script for PolyMC Python API.

For modern installations, this package uses pyproject.toml.
This setup.py is provided for backwards compatibility.
"""

from setuptools import setup, find_packages

setup(
    packages=find_packages(include=["polymcapi", "polymcapi.*"]),
)
