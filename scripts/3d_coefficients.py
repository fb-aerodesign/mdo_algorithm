"""
Get 3D coefficients
"""

import os

from pandera.typing import DataFrame

from utils import config  # pylint: disable=unused-import

from mdo_algorithm.disciplines.common.functions import (
    reynolds_number,
)
from mdo_algorithm.disciplines.common.models.geometries import Point

from mdo_algorithm.disciplines.aerodynamics.models.geometries import (
    Airfoil,
    SurfaceSection,
    Wing,
)
from mdo_algorithm.disciplines.aerodynamics.models.data_frame import Coefficients
from mdo_algorithm.disciplines.aerodynamics.services.xfoil import XfoilService
from mdo_algorithm.disciplines.aerodynamics.services.avl import AvlService
from mdo_algorithm.disciplines.aerodynamics.functions import (
    plot_coefficients,
    lift_coefficient_slope,
)


def main():
    """
    Get 3D coefficients
    """
    wing = Wing(
        section_array=[
            SurfaceSection(
                location=Point(0, 0, 0), chord=0.6, incremental_angle=0, airfoil=Airfoil("s1223")
            ),
            SurfaceSection(
                location=Point(0.15, 1.3, 0),
                chord=0.3,
                incremental_angle=0,
                airfoil=Airfoil("s1223"),
            ),
        ]
    )

    alpha = (0, 15, 1)

    xfoil_service = XfoilService()
    coefficients_array: list[DataFrame[Coefficients]] = [
        xfoil_service.get_coefficients(
            section.airfoil,
            **{
                "alpha": alpha,
                "reynolds": reynolds_number(18, section.chord, 700, 25),
                "iterations": 1000,
            },
        )
        for section in wing.section_array
    ]

    avl_service = AvlService()
    coefficients_array.append(
        avl_service.get_wing_coefficients(
            wing=wing, xfoil_coefficients_array=coefficients_array, alpha=alpha
        )
    )
    print(lift_coefficient_slope(coefficients_array[-1]))
    results_folder = os.path.join(os.path.dirname(__file__), "3d_coefficients")
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)
    for i, coefficients in enumerate(coefficients_array):
        name = coefficients.attrs.get("name", f"coefficients_{i + 1}")
        coefficients.to_csv(os.path.join(results_folder, f"{name}.csv"))
    plot_coefficients(coefficients_array)


if __name__ == "__main__":
    main()
