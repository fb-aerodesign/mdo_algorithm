"""
This script tests the aerodynamics module
"""

from pandera.typing import DataFrame

from mdo_algorithm.disciplines.aerodynamics.models import Airfoil
from mdo_algorithm.disciplines.aerodynamics.services.xfoil import XfoilService, Coefficients

xfoil_service = XfoilService(
    alpha=(0, 20, 1),
    reynolds=5e5,
    iterations=1000,
    debug=True,
)
coefficients_array: list[DataFrame[Coefficients]] = []
coefficients_array.append(xfoil_service.get_coefficients(Airfoil("fx74modsm")))
coefficients_array.append(xfoil_service.get_coefficients(Airfoil("s1223")))
xfoil_service.plot_coefficients(coefficients_array)
