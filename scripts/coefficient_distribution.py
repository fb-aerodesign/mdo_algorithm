"""
Get the coefficient distribution
"""

import os

from pandera.typing import DataFrame

from utils import config  # pylint: disable=unused-import

from mdo_algorithm.disciplines.common.constants import GRAVITATIONAL_ACCELERATION
from mdo_algorithm.disciplines.common.functions import (
    reynolds_number,
    air_density,
)
from mdo_algorithm.disciplines.common.models.geometries import (
    Point,
    MassProperties,
)

from mdo_algorithm.disciplines.aerodynamics.models.geometries import (
    Airfoil,
    SurfaceSection,
    Wing,
)
from mdo_algorithm.disciplines.aerodynamics.models.data_frame import (
    Coefficients,
    CoefficientDistribution,
)
from mdo_algorithm.disciplines.aerodynamics.services.xfoil import XfoilService
from mdo_algorithm.disciplines.aerodynamics.services.avl import AvlService
from mdo_algorithm.disciplines.aerodynamics.functions import plot_coefficient_distribution


def main():
    """
    Get the lift coefficient distribution
    """
    wing = Wing(
        section_array=[
            SurfaceSection(
                location=Point(0, 0, 0), chord=0.252, incremental_angle=0, airfoil=Airfoil("n0009")
            ),
            SurfaceSection(
                location=Point(0, 0.383, 0),
                chord=0.252,
                incremental_angle=0,
                airfoil=Airfoil("n0009"),
            ),
        ],
        mass_properties=MassProperties(),
    )

    alpha = (-5, 10, 0.5)

    xfoil_service = XfoilService()
    coefficients_array: list[DataFrame[Coefficients]] = [
        xfoil_service.get_coefficients(
            section.airfoil,
            **{
                "alpha": alpha,
                "reynolds": reynolds_number(18, section.chord, 660, 20),
                "iterations": 1000,
            },
        )
        for section in wing.section_array
    ]

    parameters = {
        "air_density": air_density(660),
        "gravitational_acceleration": GRAVITATIONAL_ACCELERATION,
    }

    avl_service = AvlService()
    distribution_array: list[DataFrame[CoefficientDistribution]] = []
    distribution_array.append(
        avl_service.get_wing_coefficient_distribution(
            wing,
            coefficients_array,
            alpha=-7,
            **parameters,
        )
    )
    distribution_array.append(
        avl_service.get_wing_coefficient_distribution(
            wing,
            coefficients_array,
            alpha=3,
            **parameters,
        )
    )
    distribution_array.append(
        avl_service.get_wing_coefficient_distribution(
            wing, coefficients_array, alpha=-3, bank_angle=30, **parameters
        )
    )
    results_folder = os.path.join(os.path.dirname(__file__), "coefficient_distribution")
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)
    distribution_array[0].to_csv(os.path.join(results_folder, "nivelado.csv"))
    distribution_array[1].to_csv(os.path.join(results_folder, "arfagem.csv"))
    distribution_array[2].to_csv(os.path.join(results_folder, "curva.csv"))
    plot_coefficient_distribution(distribution_array, ["Nivelado", "Arfagem", "Curva"])


if __name__ == "__main__":
    main()
