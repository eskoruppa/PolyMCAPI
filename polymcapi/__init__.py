"""
PolyMC Python API
=================

A lightweight Python interface for running PolyMC simulations.
"""

__version__ = "0.1.0"
__author__ = "Claude"

from .polymc import PolyMC, PolyMCError, PolyMCExecutableError

__all__ = ["PolyMC", "PolyMCError", "PolyMCExecutableError"]
