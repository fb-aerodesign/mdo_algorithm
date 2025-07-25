"""
This module provides services to interact with AVL for aerodynamic analysis.
"""

import os
import subprocess
import re
import io

import numpy as np
import pandas as pd
from pandera.typing import DataFrame

from mdo_algorithm.disciplines.aerodynamics.constants import AVL_PATH
from mdo_algorithm.disciplines.aerodynamics.models.geometries import Wing
from mdo_algorithm.disciplines.aerodynamics.models.data_frame import (
    Coefficients,
    LiftCoefficientDistribution,
)
from mdo_algorithm.disciplines.aerodynamics.models.avl import (
    GeometryInput,
    MassInput,
)


class AvlService:
    """
    AVL service class
    """

    def __init__(self):
        """
        Initialize AVL service
        """
        self.__geometry_input_file_path = os.path.join(AVL_PATH, "input.avl")
        self.__mass_input_file_path = os.path.join(AVL_PATH, "input.mass")
        self.__result_file_path = os.path.join(AVL_PATH, "result.txt")

    def run_avl(self, commands: list[str]) -> None:
        """
        Run AVL with the specified commands.

        :param commands: A list of commands to pass to XFOIL.
        :type commands: list[str]
        """
        if not os.path.exists(os.path.join(os.getcwd(), self.__geometry_input_file_path)):
            raise FileNotFoundError("AVL input file not found")
        with subprocess.Popen(
            [os.path.join(AVL_PATH, "avl.exe"), self.__geometry_input_file_path],
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
        length_unit_meters: float = 1,
        mass_unit_kilograms: float = 1,
        time_unit_seconds: float = 1,
        gravitational_acceleration: float | None = None,
        air_density: float | None = None,
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
        geometry_input = GeometryInput.from_wing(wing, xfoil_coefficients_array)
        with open(
            os.path.join(os.getcwd(), self.__geometry_input_file_path), "w", encoding="utf-8"
        ) as f:
            geometry_input.to_avl(f)
        mass_input = MassInput.from_wing(
            wing,
            length_unit_meters=length_unit_meters,
            mass_unit_kilograms=mass_unit_kilograms,
            time_unit_seconds=time_unit_seconds,
            gravitational_acceleration=gravitational_acceleration,
            air_density=air_density,
        )
        with open(
            os.path.join(os.getcwd(), self.__mass_input_file_path), "w", encoding="utf-8"
        ) as f:
            mass_input.to_mass(f)
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
        os.remove(self.__geometry_input_file_path)
        os.remove(self.__mass_input_file_path)
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
        df.attrs["name"] = (
            f"avl_3d_{wing.section_array[0].airfoil.name}_s{round(wing.planform_area(), 3)}"
            f"_cmac{round(wing.mean_aerodynamic_chord(), 3)}_b{round(wing.span(), 3)}"
        ).replace("+", "")
        return df

    def get_wing_lift_coefficient_distribution(
        self,
        wing: Wing,
        xfoil_coefficients_array: list[DataFrame[Coefficients]],
        alpha: float = 0,
        bank_angle: float = 0,
        length_unit_meters: float = 1,
        mass_unit_kilograms: float = 1,
        time_unit_seconds: float = 1,
        gravitational_acceleration: float | None = None,
        air_density: float | None = None,
    ) -> DataFrame[LiftCoefficientDistribution]:
        """
        Get the wing lift coefficient distribution using AVL.
        """
        geometry_input = GeometryInput.from_wing(wing, xfoil_coefficients_array)
        with open(
            os.path.join(os.getcwd(), self.__geometry_input_file_path), "w", encoding="utf-8"
        ) as f:
            geometry_input.to_avl(f)
        mass_input = MassInput.from_wing(
            wing,
            length_unit_meters=length_unit_meters,
            mass_unit_kilograms=mass_unit_kilograms,
            time_unit_seconds=time_unit_seconds,
            gravitational_acceleration=gravitational_acceleration,
            air_density=air_density,
        )
        with open(
            os.path.join(os.getcwd(), self.__mass_input_file_path), "w", encoding="utf-8"
        ) as f:
            mass_input.to_mass(f)
        commands = [
            "OPER",
            f"A A {alpha}",
            "X",
            "C1",
            f"B {bank_angle}",
            "",
            "X",
            f"FS {self.__result_file_path}",
            "",
            "QUIT",
        ]
        self.run_avl(commands)
        with open(os.path.join(os.getcwd(), self.__result_file_path), "r", encoding="utf-8") as f:
            content = f.read()
        os.remove(self.__geometry_input_file_path)
        os.remove(self.__mass_input_file_path)
        os.remove(self.__result_file_path)
        table_header = " Strip Forces referred to Strip Area, Chord\n"
        first_table_start = content.find(table_header) + len(table_header)
        first_table_end = first_table_start + content[first_table_start:].find("\n\n")
        second_table_start = (
            first_table_end + content[first_table_end:].find(table_header) + len(table_header)
        )
        second_table_end = second_table_start + content[second_table_start:].find("\n --")
        df1 = pd.read_fwf(io.StringIO(content[first_table_start:first_table_end])).astype(float)
        df2 = pd.read_fwf(io.StringIO(content[second_table_start:second_table_end])).astype(float)
        df = DataFrame[LiftCoefficientDistribution](
            pd.DataFrame(
                {
                    "spanwise_location": pd.concat([df1["Yle"], df2["Yle"]], ignore_index=True),
                    "lift_coefficient": pd.concat([df1["cl"], df2["cl"]], ignore_index=True),
                }
            ).sort_values("spanwise_location")
        )
        legend = [
            f"Airfoil {wing.section_array[0].airfoil.name}",
            f"S={round(wing.planform_area(), 3)}m²",
            f"Cmac={round(wing.mean_aerodynamic_chord(), 3)}m",
            f"B={round(wing.span(), 3)}m",
            f"α={alpha}°",
            f"Φ={bank_angle}°",
        ]
        if wing.mass_properties.mass > 0:
            legend.append(f"m={round(wing.mass_properties.mass, 3)}kg")
        if air_density is not None:
            legend.append(f"ρ={round(air_density, 3)}kg/m³")
        if gravitational_acceleration is not None:
            legend.append(f"g={round(gravitational_acceleration, 3)}m/s²")
        df.attrs["legend"] = " | ".join(legend)
        return df
