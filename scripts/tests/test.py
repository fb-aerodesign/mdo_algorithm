"""
This script tests the aerodynamics module
"""

from mdo_algorithm.disciplines.aerodynamics import (
    Airfoil,
    Wing,
)

airfoil = Airfoil("s1223")
wing = Wing(airfoil)
