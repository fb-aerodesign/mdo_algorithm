"""
This script tests the XFOIL tools
"""

from mdo_algorithm.disciplines.common.functions import (
    reynolds_number,
)

from mdo_algorithm.disciplines.aerodynamics.models.geometries import Airfoil
from mdo_algorithm.disciplines.aerodynamics.services.xfoil import XfoilService

analysis_parameters = {
    "alpha": (-5, 20, 0.5),
    "reynolds": reynolds_number(18, 0.6, 660, 20),
    "iterations": 1000,
}

xfoil_service = XfoilService()
coefficients = xfoil_service.get_coefficients(Airfoil("s1223"), **analysis_parameters)

cl1 = coefficients["Cl"].min()
cd1 = coefficients.at[coefficients["Cl"].idxmin(), "Cd"]
cl2 = coefficients.loc[coefficients["alpha"] == 0, "Cl"].values[0]
cd2 = coefficients.loc[coefficients["alpha"] == 0, "Cd"].values[0]
cl3 = coefficients["Cl"].max()
cd3 = coefficients.loc[coefficients["Cl"].idxmax(), "Cd"]

print(cl1)
print(cd1)
print(cl2)
print(cd2)
print(cl3)
print(cd3)
