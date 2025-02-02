"""
Aerodynamics models
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
    Airfoil dataclass
    """

    name: str


@dataclass
class WingSection:
    """
    WingSection dataclass
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
    Wing dataclass
    """

    sections: list[WingSection] = field(default_factory=list)

    def span(self) -> float:
        """
        Calculate the span of the wing
        """
        return 2 * max(s.y for s in self.sections)

    def planform_area(self) -> float:
        """
        Calculate the planform area of the wing
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
        """
        sections = sorted(self.sections, key=lambda x: x.y)
        ys = np.array([s.y for s in sections])
        chords = np.array([s.chord for s in sections])
        return np.interp(y, ys, chords)

    def chord_slope(self, y: float) -> float:
        """
        Estimate the local slope dx/dy at a given y position using linear interpolation.
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
        Generate AVL input
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
