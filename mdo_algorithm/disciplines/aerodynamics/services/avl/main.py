"""
This module provides services to interact with AVL for aerodynamic analysis.
"""

import os
import subprocess
import re

import numpy as np
import pandas as pd
from pandera.typing import DataFrame

from mdo_algorithm.disciplines.common.models.geometries import Xyz
from mdo_algorithm.disciplines.aerodynamics.constants import AVL_PATH
from mdo_algorithm.disciplines.aerodynamics.models.geometries import Wing
from mdo_algorithm.disciplines.aerodynamics.models.data import Coefficients
from mdo_algorithm.disciplines.aerodynamics.models.avl import (
    Symmetry,
    ProfileDragSettings,
    Section,
    Surface,
    Header,
    Input,
)
from mdo_algorithm.disciplines.aerodynamics.functions import cl_alpha_slope


class AvlService:
    """
    AVL service class
    """

    def __init__(self):
        """
        Initialize AVL service
        """
        self.__input_file_path = os.path.join(AVL_PATH, "input.avl")
        self.__result_file_path = os.path.join(AVL_PATH, "result.txt")

    def run_avl(self, commands: list[str]) -> None:
        """
        Run AVL with the specified commands.

        :param commands: A list of commands to pass to XFOIL.
        :type commands: list[str]
        """
        if not os.path.exists(os.path.join(os.getcwd(), self.__input_file_path)):
            raise FileNotFoundError("AVL input file not found")
        with subprocess.Popen(
            [os.path.join(AVL_PATH, "avl.exe"), self.__input_file_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ) as avl_process:
            avl_process.communicate("\n".join(commands))

    def get_wing_coefficients(
        self,
        wing: Wing,
        xfoil_coefficients_array: list[DataFrame[Coefficients]],
        alpha: list[float] | tuple[float, float, float],
    ) -> DataFrame[Coefficients]:
        """
        Get the wing coefficients using AVL.

        :param wing: The wing to analyze.
        :type wing: Wing

        :param xfoil_coefficients_array: A list of DataFrames containing the XFOIL coefficients for
        each wing section.
        :type xfoil_coefficients_array: list[DataFrame[Coefficients]]

        :param alpha: Angles of attack. Can be a list of angles or a tuple specifying the range
        (start, end, increment).
        :type alpha: list[float] | tuple[float, float, float]

        :return: DataFrame containing the aerodynamic coefficients.
        :rtype: DataFrame[Coefficients]
        """
        if len(wing.section_array) != len(xfoil_coefficients_array):
            raise ValueError(
                "The number of wing sections must be equal to the number of XFOIL coefficients"
            )
        avl_input = Input(
            header=Header(
                title="Plane",
                default_mach_number=0,
                y_symmetry=Symmetry.IGNORE,
                z_symmetry=Symmetry.IGNORE,
                xy_plane_location=0,
                reference_area=round(wing.planform_area(), 3),
                reference_chord=round(wing.mean_aerodynamic_chord(), 3),
                reference_span=wing.span(),
                default_location=Xyz(0, 0, 0),
                default_profile_drag_coefficient=None,
            ),
            surface_array=[
                Surface(
                    name="Wing",
                    chordwise_vortice_count=12,
                    chordwise_vortex_spacing=1,
                    spanwise_vortice_count=20,
                    spanwise_vortex_spacing=-1.5,
                    mirror_surface=True,
                    xz_plane_location=0,
                    scale=None,
                    translate=None,
                    incremental_angle=None,
                    ignore_wake=False,
                    ignore_freestream_effect=False,
                    ignore_load_contribution=False,
                    profile_drag_settings=None,
                    section_array=[
                        Section(
                            location=wing_section.location,
                            chord=wing_section.chord,
                            incremental_angle=wing_section.incremental_angle,
                            spanwise_vortice_count=None,
                            spanwise_vortex_spacing=None,
                            airfoil=wing_section.airfoil,
                            control_array=[],
                            cl_alpha_slope_scaling=round(
                                cl_alpha_slope(xfoil_coefficients_array[i]) / (2 * np.pi), 3
                            ),
                            profile_drag_settings=ProfileDragSettings.from_xfoil_coefficients(
                                xfoil_coefficients_array[i]
                            ),
                        )
                        for i, wing_section in enumerate(wing.section_array)
                    ],
                )
            ],
            body_array=[],
        )
        with open(os.path.join(os.getcwd(), self.__input_file_path), "w", encoding="utf-8") as f:
            f.write(avl_input.to_input_file())
        commands = ["OPER"]
        append = False
        if isinstance(alpha, tuple):
            alpha = [float(v) for v in np.arange(alpha[0], alpha[1] + 1, alpha[2])]
        for v in alpha:
            commands.extend([f"A A {v}", "X", f"FT {self.__result_file_path}"])
            if append:
                commands.append("A")
            append = True
        commands.extend(["", "QUIT"])
        self.run_avl(commands)
        with open(os.path.join(os.getcwd(), self.__result_file_path), "r", encoding="utf-8") as f:
            content = f.read()
        pattern = re.compile(
            r"Alpha\s*=\s*([-0-9.]+).*?"
            r"CLtot\s*=\s*([-0-9.]+).*?"
            r"CDtot\s*=\s*([-0-9.]+).*?"
            r"Cmtot\s*=\s*([-0-9.]+)",
            re.DOTALL,
        )
        data = {
            key: pd.Series(array, dtype=float)
            for key, array in zip(
                Coefficients.to_schema().columns.keys(), zip(*pattern.findall(content))
            )
        }
        os.remove(self.__input_file_path)
        os.remove(self.__result_file_path)
        df = DataFrame[Coefficients](pd.DataFrame(data))
        df.attrs["legend"] = " | ".join(
            [
                "AVL",
                "3D Wing",
                f"Airfoil {wing.section_array[0].airfoil.name}",
                f"S={round(wing.planform_area(), 3)}m²",
                f"Cmac={round(wing.mean_aerodynamic_chord(), 3)}m",
                f"B={round(wing.span(), 3)}m",
            ]
        )
        return df
