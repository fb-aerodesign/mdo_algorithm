"""
This module provides services to interact with XFOIL for aerodynamic analysis.
"""

import os
import subprocess

import pandas as pd
import pandera as pa
from pandera.typing import DataFrame, Index, Series

import matplotlib.pyplot as plt

from mdo_algorithm.disciplines.aerodynamics.models import Airfoil

XFOIL_PATH = os.path.join("mdo_algorithm", "softwares", "xfoil")
AIRFOILS_PATH = os.path.join("mdo_algorithm", "disciplines", "aerodynamics", "airfoils")


class Coefficients(pa.DataFrameModel):
    """
    DataFrame model for aerodynamic coefficients.
    """

    idx: Index[int]
    alpha: Series[float]
    Cl: Series[float]
    Cd: Series[float]
    Cd_pressure: Series[float]
    Cm: Series[float]


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
        airfoil_path = os.path.join(AIRFOILS_PATH, f"{airfoil.name}.dat")
        result_file_path = os.path.join(XFOIL_PATH, "result.txt")
        commands = [f"LOAD {airfoil_path}"]
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
                colspecs=[(2, 8), (10, 17), (19, 27), (29, 37), (39, 46)],
                names=["alpha", "Cl", "Cd", "Cd_pressure", "Cm"],
                dtype={
                    "alpha": float,
                    "Cl": float,
                    "Cd": float,
                    "Cd_pressure": float,
                    "Cm": float,
                },
                skiprows=12,
            )
        )
        df.attrs["airfoil"] = airfoil.name
        df.attrs["reynolds"] = reynolds
        os.remove(result_file_path)
        return df

    def plot_coefficients(self, coefficients_array: list[DataFrame[Coefficients]]) -> None:
        """
        Plot the aerodynamic coefficients.

        :param coefficients_array: List of DataFrames containing the aerodynamic coefficients.
        :type coefficients_array: list[DataFrame[Coefficients]]
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
        fig.suptitle("Coefficients")
        for coefficients in coefficients_array:
            airfoil: str = coefficients.attrs["airfoil"]
            re: float | None = coefficients.attrs["reynolds"]
            label = " | ".join([airfoil, f"Re{re:.3e}" if re is not None else "Inviscid"])
            ax1.plot(coefficients["alpha"], coefficients["Cl"], label=label)
            ax2.plot(coefficients["alpha"], coefficients["Cd"], label=label)
            ax3.plot(coefficients["alpha"], coefficients["Cm"], label=label)
            ax4.plot(coefficients["alpha"], coefficients["Cl"] / coefficients["Cd"], label=label)
        ax1.set_title("Cl x alpha")
        ax1.legend()
        ax2.set_title("Cd x alpha")
        ax2.legend()
        ax3.set_title("Cm x alpha")
        ax3.legend()
        ax4.set_title("Cl/Cd x alpha")
        ax4.legend()
        plt.show()
