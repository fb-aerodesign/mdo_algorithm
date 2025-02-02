"""
Aerodynamics models

This module defines classes for representing airfoils, wing sections, and complete wings.
It includes geometric calculations essential for aircraft design, such as span, 
planform area, and mean geometric chord.
"""

import os
from dataclasses import dataclass, field
from typing import Literal

import numpy as np
from scipy.integrate import quad

from mdo_algorithm.disciplines.aerodynamics.constants import AIRFOILS_PATH


@dataclass
class Airfoil:
    """
    Represents an airfoil by its name.

    :param name: Name of the airfoil, used to load aerodynamic profile files.
    :type name: str
    """

    name: str


@dataclass
class WingSection:
    """
    Represents a section of the wing.

    :param x: Position of the section along the x-axis.
    :type x: float

    :param y: Position of the section along the y-axis.
    :type y: float

    :param z: Position of the section along the z-axis.
    :type z: float

    :param chord: Local aerodynamic chord length.
    :type chord: float

    :param twist: Twist angle of the section.
    :type twist: float

    :param airfoil: Instance of the airfoil associated with the section.
    :type airfoil: Airfoil
    """

    x: float
    y: float
    z: float
    chord: float
    twist: float
    airfoil: Airfoil


@dataclass
class Wing:
    """
    Represents a wing composed of multiple sections.
    Contains methods to calculate geometric parameters.
    """

    sections: list[WingSection] = field(default_factory=list)

    def span(self) -> float:
        """
        Compute the total wingspan.

        :return: Wingspan in meters.
        :rtype: float
        """
        return 2 * max(s.y for s in self.sections)

    def planform_area(self) -> float:
        """
        Compute the wing planform area using the average chord of the sections.

        :return: Planform area in square meters.
        :rtype: float
        """
        sections = sorted(self.sections, key=lambda x: x.y)
        sections = [(sections[i], sections[i + 1]) for i in range(len(sections) - 1)]
        return 2 * np.sum(
            [
                0.5 * (s1.chord + s2.chord) * np.sqrt((s2.y - s1.y) ** 2 + (s2.x - s1.x) ** 2)
                for s1, s2 in sections
            ]
        )

    def chord_distribution(self, y: float) -> float:
        """
        Interpolate chord length at given y position.

        :param y: Spanwise position.
        :type y: float

        :return: Interpolated chord length.
        :rtype: float
        """
        sections = sorted(self.sections, key=lambda x: x.y)
        ys = np.array([s.y for s in sections])
        chords = np.array([s.chord for s in sections])
        return np.interp(y, ys, chords)

    def chord_slope(self, y: float) -> float:
        """
        Estimate the local slope dx/dy at a given y position using linear interpolation.

        :param y: Spanwise position.
        :type y: float

        :return: Local chord slope.
        :rtype: float
        """
        sections = sorted(self.sections, key=lambda x: x.y)
        ys = np.array([s.y for s in sections])
        xs = np.array([s.x for s in sections])
        result = 0
        if len(ys) > 1:
            slopes = np.gradient(xs, ys)
            result = np.interp(y, ys, slopes)
        return result

    def mean_geometric_chord(self) -> float:
        """
        Calculate the mean geometric chord using integration, accounting for x-offset.

        :return: Mean geometric chord in meters.
        :rtype: float
        """
        s = self.planform_area()

        def integrand(y):
            return self.chord_distribution(y) ** 2 * np.sqrt(1 + self.chord_slope(y) ** 2)

        y_min, y_max = min(s.y for s in self.sections), max(s.y for s in self.sections)
        result = 0
        if y_max != y_min:
            cmg_numerator, _ = quad(integrand, y_min, y_max)
            result = (2 / s) * cmg_numerator if s > 0 else 0
        return result

    def to_avl(
        self,
        plane_name: str = "Plane",
        wing_name: str = "Wing",
        mach: float = 0,
        iysym: Literal[-1, 0, 1] = 1,
        izsym: Literal[-1, 0, 1] = 0,
        zsym: float = 0,
        profile_drag_coefficient: float = 0,
    ) -> str:
        """
        Generate an AVL input.

        :return: Formatted string in AVL format.
        :rtype: str
        """
        if len(self.sections) < 2:
            raise RuntimeError("The wing must have at least 2 sections")
        sections = sorted(self.sections, key=lambda x: x.y)
        lines = [
            plane_name,
            str(round(mach, 5)),
            f"{iysym} {izsym} {zsym}",
            " ".join(
                [
                    str(round(self.planform_area(), 3)),
                    str(round(self.mean_geometric_chord(), 3)),
                    str(round(self.span(), 3)),
                ]
            ),
            " ".join(
                [
                    str(round(self.mean_geometric_chord() / 4, 3)),
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
