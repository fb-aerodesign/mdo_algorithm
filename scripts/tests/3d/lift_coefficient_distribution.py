"""
Get the lift coefficient distribution
"""

from pandera.typing import DataFrame

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
from mdo_algorithm.disciplines.aerodynamics.models.data_frame import Coefficients
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
                location=Point(0.15, 1.15, 0),
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
                "reynolds": reynolds_number(15, section.chord, 660, 20),
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
    lift_distribution_array = []
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
    plot_lift_distribution(lift_distribution_array, ["Nivelado", "Arfagem", "Curva"])


if __name__ == "__main__":
    main()
