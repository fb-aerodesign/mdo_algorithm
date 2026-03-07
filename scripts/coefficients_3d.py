"""
Get 3D coefficients
"""

from pandera.typing import DataFrame

from utils import config  # pylint: disable=unused-import

# from mdo_algorithm.disciplines.common.functions import (
#     reynolds_number,
# )
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
                location=Point(0, 0, 0), chord=1, incremental_angle=0, airfoil=Airfoil("s1223")
            ),
            SurfaceSection(
                location=Point(0.15, 0.9, 0),
                chord=0.7,
                incremental_angle=0,
                airfoil=Airfoil("s1223"),
            ),
        ],
    )

    alpha = (-5, 20, 0.5)

    xfoil_service = XfoilService()
    coefficients_array: list[DataFrame[Coefficients]] = [
        xfoil_service.get_coefficients(
            section.airfoil,
            **{
                "alpha": alpha,
                "reynolds": 1.1e6,
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
    plot_coefficients(coefficients_array[-1:])

    coefficients = coefficients_array[-1]

    aoa0 = coefficients.loc[coefficients["alpha"] == 0]
    aoa_stall = 14
    aoamax = coefficients.loc[coefficients["alpha"] == aoa_stall]

    cl_aoa0 = aoa0["lift_coefficient"].values[0]
    cd_aoa0 = aoa0["drag_coefficient"].values[0]
    cm_aoa0 = aoa0["moment_coefficient"].values[0]
    cl_aoamax = aoamax["lift_coefficient"].values[0]
    cd_aoamax = aoamax["drag_coefficient"].values[0]
    cl_slope = lift_coefficient_slope(coefficients)

    print(f"CL com AoA = 0°: {cl_aoa0}")
    print(f"CD com AoA = 0°: {cd_aoa0}")
    print(f"AoA máximo (ângulo de stall): {aoa_stall}°")
    print(f"CL máximo: {cl_aoamax}")
    print(f"CD máximo: {cd_aoamax}")
    print(f"Inclinação da curva CL: {cl_slope}")
    print(f"CM no c/4 com AoA = 0°: {cm_aoa0}")


if __name__ == "__main__":
    main()
