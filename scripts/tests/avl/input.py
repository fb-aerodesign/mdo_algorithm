"""
Get AVL input file
"""

import os
import argparse

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
from mdo_algorithm.disciplines.aerodynamics.models.dataframe import Coefficients
from mdo_algorithm.disciplines.aerodynamics.models.avl import (
    GeometryInput,
    MassInput,
)
from mdo_algorithm.disciplines.aerodynamics.services.xfoil import XfoilService

parser = argparse.ArgumentParser(description="Get AVL input file")
parser.add_argument("--output", "-o", help="Output file path", default="input.avl")
args = parser.parse_args()


def main():
    """
    Get AVL input file
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

    geometry_input = GeometryInput.from_wing(wing, coefficients_array)
    mass_input = MassInput.from_wing(
        wing, gravitational_acceleration=GRAVITATIONAL_ACCELERATION, air_density=air_density(660)
    )
    with open(os.path.join(os.getcwd(), "input.avl"), "w", encoding="utf-8") as f:
        geometry_input.to_avl(f)
    with open(os.path.join(os.getcwd(), "input.mass"), "w", encoding="utf-8") as f:
        mass_input.to_mass(f)


if __name__ == "__main__":
    main()
