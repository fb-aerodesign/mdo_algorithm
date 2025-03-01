"""
This module provides services to interact with XFOIL for aerodynamic analysis.
"""

import os
import subprocess

import pandas as pd
from pandera.typing import DataFrame

from mdo_algorithm.disciplines.aerodynamics.constants import XFOIL_PATH
from mdo_algorithm.disciplines.aerodynamics.models.geometries import Airfoil
from mdo_algorithm.disciplines.aerodynamics.models.dataframe import Coefficients


class XfoilService:
    """
    Service class to interact with XFOIL for aerodynamic analysis.
    """

    def __init__(self) -> None:
        """
        Initialize the XfoilService.
        """

    def run_xfoil(self, commands: list[str]) -> None:
        """
        Run XFOIL with the specified commands.

        :param commands: A list of commands to pass to XFOIL.
        :type commands: list[str]
        """
        with subprocess.Popen(
            [os.path.join(XFOIL_PATH, "xfoil.exe")],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ) as xfoil_process:
            xfoil_process.communicate("\n".join(commands))

    def get_coefficients(
        self,
        airfoil: Airfoil,
        alpha: list[float] | tuple[float, float, float],
        reynolds: float | None,
        iterations: int | None,
    ) -> DataFrame[Coefficients]:
        """
        Get aerodynamic coefficients for a given airfoil and angle of attack.

        :param airfoil: The airfoil to analyze.
        :type airfoil: Airfoil

        :param alpha: Angles of attack. Can be a list of angles or a tuple specifying the range
        (start, end, increment).
        :type alpha: list[float] | tuple[float, float, float]

        :param reynolds: Reynolds number.
        :type reynolds: float | None

        :param iterations: Number of iterations for XFOIL.
        :type iterations: int | None

        :return: DataFrame containing the aerodynamic coefficients.
        :rtype: DataFrame[Coefficients]
        """
        result_file_path = os.path.join(XFOIL_PATH, "result.txt")
        commands = [f"LOAD {airfoil.relative_path()}"]
        commands.append("PANE")
        commands.append("OPER")
        if reynolds is not None:
            commands.append(f"VISC {reynolds}")
            if iterations is not None:
                commands.append(f"ITER {iterations}")
        commands.append("PACC")
        commands.append(result_file_path)
        commands.append("")
        if isinstance(alpha, list):
            for v in alpha:
                commands.append(f"ALFA {v}")
        else:
            commands.append(f"ASEQ {alpha[0]} {alpha[1]} {alpha[2]}")
        commands.append("PACC")
        commands.append("")
        commands.append("QUIT")
        self.run_xfoil(commands)
        result_file_path = os.path.join(os.getcwd(), result_file_path)
        df = DataFrame[Coefficients](
            pd.read_fwf(
                result_file_path,
                colspecs=[(2, 8), (10, 17), (19, 27), (39, 46)],
                names=["alpha", "lift_coefficient", "drag_coefficient", "moment_coefficient"],
                dtype={
                    "alpha": float,
                    "lift_coefficient": float,
                    "drag_coefficient": float,
                    "moment_coefficient": float,
                },
                skiprows=12,
            )
        )
        df.attrs["legend"] = " | ".join(
            [
                "XFOIL",
                "2D",
                f"Airfoil {airfoil.name}",
                f"Re={reynolds:.3e}" if reynolds is not None else "Inviscid",
            ]
        )
        os.remove(result_file_path)
        return df
