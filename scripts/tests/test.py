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
results = []
results.append(xfoil_service.get_coefficients(Airfoil("fx74modsm")))
results.append(xfoil_service.get_coefficients(Airfoil("s1223")))

coefficients_array: list[DataFrame[Coefficients]] = [v for v in results if v is not None]

xfoil_service.plot_coefficients(coefficients_array)
