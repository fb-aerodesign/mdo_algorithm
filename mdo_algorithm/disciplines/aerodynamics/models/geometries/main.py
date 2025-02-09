"""
Aerodynamics geometry models

This module defines classes for representing airfoils, wing sections, and complete wings.
It includes geometric calculations essential for aircraft design, such as span, 
planform area, and mean geometric chord.
"""

import os
from dataclasses import dataclass, field

import numpy as np
from scipy.integrate import quad

from mdo_algorithm.disciplines.common.models.geometries import Xyz
from mdo_algorithm.disciplines.aerodynamics.constants import AIRFOILS_PATH


@dataclass
class Airfoil:
    """
    Represents an airfoil by its name.

    :param name: Name of the airfoil, used to load aerodynamic profile files.
    :type name: str
    """

    name: str

    def relative_path(self):
        """
        Airfoil's file relative path
        """
        return os.path.join(AIRFOILS_PATH, self.name)


@dataclass
class WingSection:
    """
    Represents a section of the wing.

    :param leading_edge_location: Location of the airfoil's leading edge
    :type leading_edge_location: Xyz

    :param chord: Local aerodynamic chord length.
    :type chord: float

    :param twist: Twist angle of the section.
    :type twist: float

    :param airfoil: Instance of the airfoil associated with the section.
    :type airfoil: Airfoil
    """

    location: Xyz
    chord: float
    twist: float
    airfoil: Airfoil


@dataclass
class Wing:
    """
    Represents a wing composed of multiple sections.
    Contains methods to calculate geometric parameters.
    """

    section_array: list[WingSection] = field(default_factory=list)

    def span(self) -> float:
        """
        Compute the total wingspan.

        :return: Wingspan in meters.
        :rtype: float
        """
        return 2 * max(s.location.y for s in self.section_array)

    def planform_area(self) -> float:
        """
        Compute the wing planform area using the average chord of the sections.

        :return: Planform area in square meters.
        :rtype: float
        """
        sections = sorted(self.section_array, key=lambda x: x.location.y)
        sections = [(sections[i], sections[i + 1]) for i in range(len(sections) - 1)]
        return 2 * np.sum(
            [
                0.5
                * (s1.chord + s2.chord)
                * np.sqrt(
                    (s2.location.y - s1.location.y) ** 2 + (s2.location.x - s1.location.x) ** 2
                )
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
        sections = sorted(self.section_array, key=lambda x: x.location.y)
        ys = np.array([s.location.y for s in sections])
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
        sections = sorted(self.section_array, key=lambda x: x.location.y)
        ys = np.array([s.location.y for s in sections])
        xs = np.array([s.location.x for s in sections])
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

        y_min, y_max = min(s.location.y for s in self.section_array), max(
            s.location.y for s in self.section_array
        )
        result = 0
        if y_max != y_min:
            cmg_numerator, _ = quad(integrand, y_min, y_max)
            result = (2 / s) * cmg_numerator if s > 0 else 0
        return result
