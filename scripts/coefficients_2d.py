"""
Get 2D coefficients
"""

from pandera.typing import DataFrame

from utils import config  # pylint: disable=unused-import

# from mdo_algorithm.disciplines.common.functions import (
#     reynolds_number,
# )

from mdo_algorithm.disciplines.aerodynamics.models.geometries import Airfoil
from mdo_algorithm.disciplines.aerodynamics.models.data_frame import Coefficients
from mdo_algorithm.disciplines.aerodynamics.services.xfoil import XfoilService
from mdo_algorithm.disciplines.aerodynamics.functions import (
    plot_coefficients,
    lift_coefficient_slope,
)


def main():
    """
    Get 2D coefficients
    """
    analysis_parameters = {
        "alpha": (-5, 20, 0.5),
        "reynolds": 1.1e6,
        "iterations": 1000,
    }

    xfoil_service = XfoilService()
    coefficients_array: list[DataFrame[Coefficients]] = []
    coefficients_array.append(
        xfoil_service.get_coefficients(Airfoil("s1223"), **analysis_parameters)
    )
    plot_coefficients(coefficients_array)

    coefficients = coefficients_array[0]

    aoa0 = coefficients.loc[coefficients["alpha"] == 0]
    aoamax = coefficients.loc[
        coefficients["lift_coefficient"] == max(coefficients["lift_coefficient"])
    ]
    aoa_stall = aoamax["alpha"].values[0]

    cl_aoa0 = aoa0["lift_coefficient"].values[0]
    cd_aoa0 = aoa0["drag_coefficient"].values[0]
    cm_aoa0 = aoa0["moment_coefficient"].values[0]
    cl_aoamax = aoamax["lift_coefficient"].values[0]
    cd_aoamax = aoamax["drag_coefficient"].values[0]
    cl_slope = lift_coefficient_slope(coefficients)

    print(f"Cl com AoA = 0°: {cl_aoa0}")
    print(f"Cd com AoA = 0°: {cd_aoa0}")
    print(f"AoA máximo (ângulo de stall): {aoa_stall}°")
    print(f"Cl máximo: {cl_aoamax}")
    print(f"Cd máximo: {cd_aoamax}")
    print(f"Inclinação da curva Cl: {cl_slope}")
    print(f"Cm no c/4 com AoA = 0°: {cm_aoa0}")


if __name__ == "__main__":
    main()
