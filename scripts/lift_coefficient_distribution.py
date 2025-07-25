"""
Get the lift coefficient distribution
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
    LiftCoefficientDistribution,
)
from mdo_algorithm.disciplines.aerodynamics.services.xfoil import XfoilService
from mdo_algorithm.disciplines.aerodynamics.services.avl import AvlService
from mdo_algorithm.disciplines.aerodynamics.functions import plot_lift_distribution


def main():
    """
    Get the lift coefficient distribution
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
        ],
        mass_properties=MassProperties(mass=10, center_of_gravity=Point(0.15, 0, 0)),
    )

    alpha = (-5, 20, 0.5)

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
    lift_distribution_array: list[DataFrame[LiftCoefficientDistribution]] = []
    lift_distribution_array.append(
        avl_service.get_wing_lift_coefficient_distribution(
            wing,
            coefficients_array,
            **parameters,
        )
    )
    lift_distribution_array.append(
        avl_service.get_wing_lift_coefficient_distribution(
            wing,
            coefficients_array,
            alpha=10,
            **parameters,
        )
    )
    lift_distribution_array.append(
        avl_service.get_wing_lift_coefficient_distribution(
            wing, coefficients_array, alpha=4, bank_angle=30, **parameters
        )
    )
    results_folder = os.path.join(os.path.dirname(__file__), "lift_coefficient_distribution")
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)
    lift_distribution_array[0].to_csv(os.path.join(results_folder, "nivelado.csv"))
    lift_distribution_array[1].to_csv(os.path.join(results_folder, "arfagem.csv"))
    lift_distribution_array[2].to_csv(os.path.join(results_folder, "curva.csv"))
    plot_lift_distribution(lift_distribution_array, ["Nivelado", "Arfagem", "Curva"])


if __name__ == "__main__":
    main()
