"""
Aerodynamics models
"""

from dataclasses import dataclass


@dataclass
class Airfoil:
    """
    Airfoil dataclass
    """
    name: str


@dataclass
class Wing:
    """
    Wing dataclass
    """
    airfoil: Airfoil
