"""
Get AVL input file
"""

import os
import argparse

from pandera.typing import DataFrame

from mdo_algorithm.disciplines.common.functions import reynolds_number
from mdo_algorithm.disciplines.common.models.geometries import Xyz

from mdo_algorithm.disciplines.aerodynamics.models.geometries import (
    Airfoil,
    SurfaceSection,
    Wing,
)
from mdo_algorithm.disciplines.aerodynamics.models.data import Coefficients
from mdo_algorithm.disciplines.aerodynamics.services.xfoil import XfoilService
from mdo_algorithm.disciplines.aerodynamics.services.avl import AvlService

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
    avl_input = avl_service.get_avl_input_from_wing(wing, coefficients_array)
    with open(os.path.join(os.getcwd(), args.output), "w", encoding="utf-8") as f:
        f.write(avl_input.to_input_file())


if __name__ == "__main__":
    main()
