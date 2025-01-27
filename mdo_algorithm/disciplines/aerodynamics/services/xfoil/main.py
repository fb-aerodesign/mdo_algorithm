"""
This module provides services to interact with XFOIL for aerodynamic analysis.
"""

import os
import winpty

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

    def __init__(
        self,
        alpha: list[float] | tuple[float, float, float],
        reynolds: float | None = None,
        iterations: int | None = None,
        debug: bool = False,
    ):
        """
        Initialize the XfoilService.

        :param alpha: Angles of attack. Can be a list of angles or a tuple specifying the range
        (start, end, increment).
        :type alpha: list[float] | tuple[float, float, float]

        :param reynolds: Reynolds number.
        :type reynolds: float | None

        :param iterations: Number of iterations for XFOIL.
        :type iterations: int | None

        :param debug: Toggle debug mode to print xfoil outputs
        :type debug: bool
        """
        self.__alpha = alpha
        self.__reynolds = reynolds
        self.__iterations = iterations
        self.__xfoil = winpty.PtyProcess.spawn(os.path.join(XFOIL_PATH, "xfoil.exe"))
        self.__debug = debug
        self.__first_analysis = True

    def get_coefficients(self, airfoil: Airfoil) -> DataFrame[Coefficients] | None:
        """
        Get aerodynamic coefficients for a given airfoil and angle of attack.

        :param airfoil: The airfoil to analyze.
        :type airfoil: Airfoil

        :return: DataFrame containing the aerodynamic coefficients.
        :rtype: DataFrame[Coefficients]
        """
        airfoil_path = os.path.join(AIRFOILS_PATH, f"{airfoil.name}.dat")
        result_file_path = os.path.join(XFOIL_PATH, "result.txt")
        self.__send_command(f"LOAD {airfoil_path}")
        self.__send_command("PANE")
        self.__send_command("OPER")
        if self.__reynolds is not None and self.__first_analysis:
            self.__send_command(f"VISC {self.__reynolds}")
            if self.__iterations is not None:
                self.__send_command(f"ITER {self.__iterations}")
        self.__send_command("PACC")
        self.__send_command(result_file_path)
        self.__send_command("")
        if isinstance(self.__alpha, list):
            for v in self.__alpha:
                self.__send_command(f"ALFA {v}")
        else:
            self.__send_command(f"ASEQ {self.__alpha[0]} {self.__alpha[1]} {self.__alpha[2]}")
        self.__send_command("PACC")
        self.__send_command("")
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
        os.remove(result_file_path)
        self.__first_analysis = False
        return df

    def plot_coefficients(self, coefficients_array: list[DataFrame[Coefficients]]) -> None:
        """
        Plot the aerodynamic coefficients.

        :param coefficients: DataFrame containing the aerodynamic coefficients.
        :type coefficients: DataFrame[Coefficients]
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
        title = ["Coefficients"]
        if self.__reynolds is None:
            title.append("Inviscid")
        else:
            title.append(f"Reynolds: {self.__reynolds}")
        fig.suptitle(" | ".join(title))
        for coefficients in coefficients_array:
            ax1.plot(coefficients["alpha"], coefficients["Cl"], label=coefficients.attrs["airfoil"])
            ax2.plot(coefficients["alpha"], coefficients["Cd"], label=coefficients.attrs["airfoil"])
            ax3.plot(coefficients["alpha"], coefficients["Cm"], label=coefficients.attrs["airfoil"])
            ax4.plot(
                coefficients["alpha"],
                coefficients["Cl"] / coefficients["Cd"],
                label=coefficients.attrs["airfoil"],
            )
        ax1.set_title("Cl x alpha")
        ax1.legend()
        ax2.set_title("Cd x alpha")
        ax2.legend()
        ax3.set_title("Cm x alpha")
        ax3.legend()
        ax4.set_title("Cl/Cd x alpha")
        ax4.legend()
        plt.show()

    def __send_command(self, command: str) -> str:
        self.__xfoil.write(command + "\r\n")
        if self.__debug:
            print(command)
        output = ""
        while "c>" not in output and "s>" not in output:
            output += self.__xfoil.read()
        if self.__debug:
            print(output)
        return output
