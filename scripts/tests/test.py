"""
This script tests the aerodynamics module
"""

from pandera.typing import DataFrame

from mdo_algorithm.disciplines.common.functions import (
    reynolds_number,
)

from mdo_algorithm.disciplines.aerodynamics.models import Airfoil
from mdo_algorithm.disciplines.aerodynamics.services.xfoil import XfoilService, Coefficients

params = [(0, 20, 0.5), reynolds_number(12, 1, 660, 20), 1000]

xfoil_service = XfoilService()
coefficients_array: list[DataFrame[Coefficients]] = []
coefficients_array.append(xfoil_service.get_coefficients(Airfoil("fx74modsm"), *params))
coefficients_array.append(xfoil_service.get_coefficients(Airfoil("s1223"), *params))
xfoil_service.plot_coefficients(coefficients_array)
