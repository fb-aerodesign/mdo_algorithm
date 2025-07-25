"""
Aerodynamics geometry models

This module defines classes for representing airfoils, wing sections, and complete wings.
It includes geometric calculations essential for aircraft design, such as span,
planform area, and mean aerodynamic chord.
"""

import os
from dataclasses import dataclass, field

import numpy as np
from scipy.integrate import quad

from mdo_algorithm.disciplines.common.models.geometries import (
    Point,
    MassProperties,
)
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
        return os.path.join(AIRFOILS_PATH, self.name + ".dat")


@dataclass
class SurfaceSection:
    """
    Represents a section of the lifting surface.

    :param leading_edge_location: Location of the airfoil's leading edge
    :type leading_edge_location: Point

    :param chord: Local aerodynamic chord length.
    :type chord: float

    :param incremental_angle: Twist angle of the section.
    :type twist: float

    :param airfoil: Instance of the airfoil associated with the section.
    :type airfoil: Airfoil
    """

    location: Point
    chord: float
    incremental_angle: float
    airfoil: Airfoil


@dataclass
class Wing:
    """
    Represents a wing composed of multiple sections.
    Contains methods to calculate geometric parameters.
    """

    section_array: list[SurfaceSection] = field(default_factory=list)
    mass_properties: MassProperties = field(default_factory=MassProperties)

    def span(self) -> float:
        """
        Compute the total wingspan.

        :return: Wingspan in meters.
        :rtype: float
        """
        return 2 * max(s.location.y for s in self.section_array)

    def chord_distribution(self, y: float) -> float:
        """
        Interpolate chord length at given y position.

        :param y: Spanwise position.
        :type y: float

        :return: Interpolated chord length.
        :rtype: float
        """
        sections = sorted(self.section_array, key=lambda x: x.location.y)
        return np.interp(
            y, np.array([s.location.y for s in sections]), np.array([s.chord for s in sections])
        )

    def planform_area(self) -> float:
        """
        Compute the wing planform area.

        :return: Planform area in square meters.
        :rtype: float
        """
        return 2 * quad(self.chord_distribution, 0, self.span() / 2)[0]

    def mean_aerodynamic_chord(self) -> float:
        """
        Calculate the mean aerodynamic chord.

        :return: Mean aerodynamic chord in meters.
        :rtype: float
        """
        area = self.planform_area()
        result = 0
        if area != 0:
            result = (
                2 / area * quad(lambda x: self.chord_distribution(x) ** 2, 0, self.span() / 2)[0]
            )
        return result

    def aspect_ratio(self) -> float:
        """
        Calculate the aspect ratio of the wing.

        :return: Aspect ratio (span^2 / planform area).
        :rtype: float
        """
        return self.span() ** 2 / self.planform_area() if self.planform_area() != 0 else 0
