"""
This script tests the AVL tools
"""

from mdo_algorithm.disciplines.aerodynamics.models import (
    Airfoil,
    WingSection,
    Wing,
)

test = Wing(
    sections=[
        WingSection(0, 0, 0, 0.6, 0, Airfoil("s1223")),
        WingSection(0, 1.15, 0, 0.3, 0, Airfoil("s1223")),
    ]
)

print(test.to_avl())
