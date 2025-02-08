"""
Common geometry models
"""

from dataclasses import dataclass


@dataclass
class Xyz:
    """
    Three-dimensional object
    """
    x: float
    y: float
    z: float
