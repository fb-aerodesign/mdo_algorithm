"""
Get 2D coefficients
"""

from pandera.typing import DataFrame

from mdo_algorithm.disciplines.common.functions import (
    reynolds_number,
)

from mdo_algorithm.disciplines.aerodynamics.models.geometries import Airfoil
from mdo_algorithm.disciplines.aerodynamics.models.data_frame import Coefficients
from mdo_algorithm.disciplines.aerodynamics.services.xfoil import XfoilService
from mdo_algorithm.disciplines.aerodynamics.functions import plot_coefficients


def main():
    """
    Get 2D coefficients
    """
    analysis_parameters = {
        "alpha": (0, 20, 0.5),
        "reynolds": reynolds_number(12, 0.5, 660, 20),
        "iterations": 1000,
    }

    xfoil_service = XfoilService()
    coefficients_array: list[DataFrame[Coefficients]] = []
    coefficients_array.append(
        xfoil_service.get_coefficients(Airfoil("fx74modsm"), **analysis_parameters)
    )
    coefficients_array.append(xfoil_service.get_coefficients(Airfoil("s1223"), **analysis_parameters))
    plot_coefficients(coefficients_array)


if __name__ == "__main__":
    main()
