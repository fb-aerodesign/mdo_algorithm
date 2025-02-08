"""
This module provides services to interact with AVL for aerodynamic analysis.
"""

import os
from typing import Literal

from mdo_algorithm.disciplines.aerodynamics.constants import (
    AIRFOILS_PATH,
)
from mdo_algorithm.disciplines.aerodynamics.models.geometries import Wing


class AvlService:
    """
    AVL service class
    """

    def __init__(self):
        """
        Initialize AVL service
        """

    def get_input_from_wing(
        self,
        wing: Wing,
        plane_name: str = "Plane",
        wing_name: str = "Wing",
        mach: float = 0,
        iysym: Literal[-1, 0, 1] = 1,
        izsym: Literal[-1, 0, 1] = 0,
        zsym: float = 0,
        profile_drag_coefficient: float = 0,
    ) -> str:
        """
        Get AVL input from a wing object

        :param wing: Wing object
        :type wing: Wing

        :param plane_name: Name of the plane
        :type plane_name: str

        :param wing_name: Name of the wing
        :type wing_name: str

        :param mach: Mach number
        :type mach: float

        :param iysym: Symmetry flag along the y-axis
        :type iysym: int

        :param izsym: Symmetry flag along the z-axis
        :type izsym: int

        :param zsym: Symmetry plane position
        :type zsym: float

        :param profile_drag_coefficient: Profile drag coefficient
        :type profile_drag_coefficient: float

        :return: AVL input
        :rtype: str
        """
        if len(wing.sections) < 2:
            raise RuntimeError("The wing must have at least 2 sections")
        sections = sorted(wing.sections, key=lambda x: x.y)
        lines = [
            plane_name,
            str(round(mach, 5)),
            f"{iysym} {izsym} {zsym}",
            " ".join(
                [
                    str(round(wing.planform_area(), 3)),
                    str(round(wing.mean_geometric_chord(), 3)),
                    str(round(wing.span(), 3)),
                ]
            ),
            " ".join(
                [
                    str(round(wing.mean_geometric_chord() / 4, 3)),
                    "0",
                    "0",
                ]
            ),
            str(round(profile_drag_coefficient, 5)),
            "SURFACE",
            wing_name,
        ]
        for section in sections:
            airfoil_path = os.path.join(AIRFOILS_PATH, f"{section.airfoil.name}.dat")
            lines.extend(
                [
                    "SECTION",
                    " ".join(
                        [
                            str(section.x),
                            str(section.y),
                            str(section.z),
                            str(section.chord),
                            str(section.twist),
                        ]
                    ),
                    f"AFILE {airfoil_path}",
                ]
            )
        return "\n".join(lines)
