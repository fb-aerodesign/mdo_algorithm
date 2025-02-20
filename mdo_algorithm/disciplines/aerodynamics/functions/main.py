"""
Aerodynamics functions
"""

from pandera.typing import DataFrame
import matplotlib.pyplot as plt

import numpy as np
from scipy.stats import linregress

from mdo_algorithm.disciplines.aerodynamics.models.data import Coefficients


def cl_alpha_slope(xfoil_coefficients: DataFrame[Coefficients]) -> float:
    """
    Calculate the lift coefficient slope

    :param xfoil_coefficients: XFOIL coefficients
    :type xfoil_coefficients: DataFrame[Coefficients]

    :return: Lift coefficient slope
    :rtype: float
    """

    mask = (xfoil_coefficients["alpha"] > 0) & (xfoil_coefficients["alpha"] < 5)
    alpha = xfoil_coefficients.loc[mask, "alpha"] * np.pi / 180
    cl = xfoil_coefficients.loc[mask, "lift_coefficient"]

    res = linregress(alpha, cl)

    return res.slope


def plot_coefficients(coefficients_array: list[DataFrame[Coefficients]]) -> None:
    """
    Plot the aerodynamic coefficients.

    :param coefficients_array: List of DataFrames containing the aerodynamic coefficients.
    :type coefficients_array: list[DataFrame[Coefficients]]
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
    fig.suptitle("Coefficients")
    legend = False
    for coefficients in coefficients_array:
        (line,) = ax1.plot(coefficients["alpha"], coefficients["lift_coefficient"])
        ax2.plot(coefficients["alpha"], coefficients["drag_coefficient"])
        ax3.plot(coefficients["alpha"], coefficients["moment_coefficient"])
        ax4.plot(
            coefficients["alpha"],
            coefficients["lift_coefficient"] / coefficients["drag_coefficient"],
        )
        if "legend" in coefficients.attrs:
            line.set_label(coefficients.attrs["legend"])
            legend = True
    if legend:
        fig.legend()
    ax1.set_xlabel("alpha [°]")
    ax1.set_ylabel("lift coefficient")
    ax2.set_xlabel("alpha [°]")
    ax2.set_ylabel("drag coefficient")
    ax3.set_xlabel("alpha [°]")
    ax3.set_ylabel("moment coefficient")
    ax4.set_xlabel("alpha [°]")
    ax4.set_ylabel("lift coefficient/drag coefficient")
    plt.show()


def plot_drag_polar(coefficients_array: list[DataFrame[Coefficients]]) -> None:
    """
    Plot the drag polar.

    :param coefficients_array: List of DataFrames containing the aerodynamic coefficients.
    :type coefficients_array: list[DataFrame[Coefficients]]
    """
    fig, ax = plt.subplots()
    fig.suptitle("Drag Polar")
    legend = False
    for coefficients in coefficients_array:
        (line,) = ax.plot(coefficients["lift_coefficient"], coefficients["drag_coefficient"])
        if "legend" in coefficients.attrs:
            line.set_label(coefficients.attrs["legend"])
            legend = True
    if legend:
        fig.legend()
    ax.set_xlabel("lift coefficient")
    ax.set_ylabel("drag coefficient")
    plt.show()
