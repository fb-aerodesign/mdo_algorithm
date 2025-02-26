"""
Get 3D coefficients
"""

from pandera.typing import DataFrame

from mdo_algorithm.disciplines.common.functions import (
    reynolds_number,
)
from mdo_algorithm.disciplines.common.models.geometries import Xyz

from mdo_algorithm.disciplines.aerodynamics.models.geometries import (
    Airfoil,
    SurfaceSection,
    Wing,
)
from mdo_algorithm.disciplines.aerodynamics.models.data import Coefficients
from mdo_algorithm.disciplines.aerodynamics.services.xfoil import XfoilService
from mdo_algorithm.disciplines.aerodynamics.services.avl import AvlService
from mdo_algorithm.disciplines.aerodynamics.functions import plot_coefficients


def main():
    """
    Get 3D coefficients
    """
    wing = Wing(
        section_array=[
            SurfaceSection(
                location=Xyz(0, 0, 0), chord=0.6, incremental_angle=0, airfoil=Airfoil("s1223")
            ),
            SurfaceSection(
                location=Xyz(0.15, 1.15, 0),
                chord=0.3,
                incremental_angle=0,
                airfoil=Airfoil("s1223"),
            ),
        ]
    )

    alpha = (-5, 20, 0.5)

    xfoil_service = XfoilService()
    coefficients_array: list[DataFrame[Coefficients]] = [
        xfoil_service.get_coefficients(
            section.airfoil,
            **{
                "alpha": alpha,
                "reynolds": reynolds_number(12, section.chord, 660, 20),
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
    plot_coefficients(coefficients_array)


if __name__ == "__main__":
    main()
