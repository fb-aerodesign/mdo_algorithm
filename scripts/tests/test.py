"""
This script tests the aerodynamics module
"""

from mdo_algorithm.disciplines.aerodynamics.models import Airfoil
from mdo_algorithm.disciplines.aerodynamics.services.xfoil import XfoilService

airfoil = Airfoil("s1223")

xfoil_service = XfoilService()
coefficients = xfoil_service.get_coefficients(airfoil, (-5, 20, 0.5), 5e5)
xfoil_service.plot_coefficients(coefficients)
