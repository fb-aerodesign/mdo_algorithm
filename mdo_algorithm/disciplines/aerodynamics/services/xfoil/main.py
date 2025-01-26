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

    def __init__(self):
        """
        Initialize the XfoilService with a subprocess to run XFOIL.
        """
        self.__xfoil_process = subprocess.Popen(
            [os.path.join(XFOIL_PATH, "xfoil.exe")],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

    def get_coefficients(
        self,
        airfoil: Airfoil,
        alpha: list[float] | tuple[float, float, float],
        reynolds: float,
        iterations: int = 200,
    ) -> DataFrame[Coefficients]:
        """
        Get aerodynamic coefficients for a given airfoil and angle of attack.

        :param airfoil: The airfoil to analyze.
        :type airfoil: Airfoil

        :param alpha: Angles of attack. Can be a list of angles or a tuple specifying the range
        (start, end, increment).
        :type alpha: list[float] | tuple[float, float, float]

        :param reynolds: Reynolds number.
        :type reynolds: float

        :param iterations: Number of iterations for XFOIL.
        :type iterations: int

        :return: DataFrame containing the aerodynamic coefficients.
        :rtype: DataFrame[Coefficients]
        """
        airfoil_path = os.path.join(AIRFOILS_PATH, f"{airfoil.name}.dat")
        result_file_path = os.path.join(XFOIL_PATH, "results.txt")
        commands = [
            f"LOAD {airfoil_path}",
            "PANE",
            "OPER",
            f"VISC {reynolds}",
            f"ITER {iterations}",
            "PACC",
            result_file_path,
            "",
        ]
        if isinstance(alpha, list):
            commands.extend([f"ALFA {v}" for v in alpha])
        else:
            commands.append(f"ASEQ {alpha[0]} {alpha[1]} {alpha[2]}")
        commands.append("")
        commands.append("QUIT")
        self.__xfoil_process.communicate("\n".join(commands))
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

    def plot_coefficients(self, coefficients: DataFrame[Coefficients]) -> None:
        """
        Plot the aerodynamic coefficients.

        :param coefficients: DataFrame containing the aerodynamic coefficients.
        :type coefficients: DataFrame[Coefficients]
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
        fig.suptitle(
            f"{coefficients.attrs['airfoil']} Coefficients | "
            f"Reynolds: {coefficients.attrs['reynolds']}"
        )
        ax1.plot(coefficients["alpha"], coefficients["Cl"])
        ax1.set_title("Cl x alpha")
        ax2.plot(coefficients["alpha"], coefficients["Cd"])
        ax2.set_title("Cd x alpha")
        ax3.plot(coefficients["alpha"], coefficients["Cm"])
        ax3.set_title("Cm x alpha")
        ax4.plot(coefficients["alpha"], coefficients["Cl"] / coefficients["Cd"])
        ax4.set_title("Cl/Cd x alpha")
        plt.show()
