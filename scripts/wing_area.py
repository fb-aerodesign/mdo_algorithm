"""
Get wing area
"""

from utils import config  # pylint: disable=unused-import

from mdo_algorithm.disciplines.common.models.geometries import Point

from mdo_algorithm.disciplines.aerodynamics.models.geometries import (
    Airfoil,
    SurfaceSection,
    Wing,
)


def main():
    """
    Get wing area
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
    )

    print(wing.span())
    print(wing.mean_aerodynamic_chord())
    print(wing.aspect_ratio())
    print(wing.planform_area())


if __name__ == "__main__":
    main()
