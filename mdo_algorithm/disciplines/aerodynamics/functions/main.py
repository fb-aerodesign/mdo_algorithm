"""
Aerodynamics functions
"""

from pandera.typing import DataFrame
import matplotlib.pyplot as plt

import numpy as np
from scipy.stats import linregress
from scipy.optimize import curve_fit

from mdo_algorithm.disciplines.aerodynamics.models.data_frame import (
    Coefficients,
    LiftCoefficientDistribution,
)


def lift_coefficient_slope(coefficients: DataFrame[Coefficients]) -> float:
    """
    Calculate the lift coefficient slope

    :param coefficients: Aerodynamic coefficients
    :type coefficients: DataFrame[Coefficients]

    :return: Lift coefficient slope
    :rtype: float
    """

    mask = (coefficients["alpha"] > 0) & (coefficients["alpha"] < 5)
    alpha = coefficients.loc[mask, "alpha"] * np.pi / 180
    cl = coefficients.loc[mask, "lift_coefficient"]
    return linregress(alpha, cl).slope


def lift_coefficient_quadratic_model(
    coefficients: DataFrame[Coefficients],
) -> tuple[float, float, float, float]:
    """
    Fit a quadratic model to the lift coefficient.

    :param coefficients: Aerodynamic coefficients
    :type coefficients: DataFrame[Coefficients]

    :return:
        Quadratic model coefficients

        - cd0: Zero lift drag coefficient
        - cl_cd0: Lift coefficient at zero drag
        - cd2u: Quadratic drag coefficient for upper part of the drag polar
        - cd2l: Quadratic drag coefficient for lower part of the drag polar

    :rtype: tuple[float, float, float, float]
    """
    df = coefficients.sort_values(by="lift_coefficient")
    cl = df["lift_coefficient"].values
    cd = df["drag_coefficient"].values
    cl_cd0 = cl[np.argmin(cd)]  # type: ignore
    cd0 = min(cd)
    mask_upper = cl >= cl_cd0
    mask_lower = cl < cl_cd0
    cd2u = curve_fit(
        lambda cl, cd2: cd0 + cd2 * (cl - cl_cd0) ** 2, cl[mask_upper], cd[mask_upper]
    )[0][0]
    cd2l = curve_fit(
        lambda cl, cd2: cd0 + cd2 * (cl - cl_cd0) ** 2, cl[mask_lower], cd[mask_lower]
    )[0][0]
    return cd0, float(cl_cd0), cd2u, cd2l


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
        (line,) = ax1.plot(coefficients["alpha"], coefficients["lift_coefficient"], marker="o")
        ax2.plot(coefficients["alpha"], coefficients["drag_coefficient"], marker="o")
        ax3.plot(coefficients["alpha"], coefficients["moment_coefficient"], marker="o")
        ax4.plot(
            coefficients["alpha"],
            coefficients["lift_coefficient"] / coefficients["drag_coefficient"],
            marker="o",
        )
        if "legend" in coefficients.attrs:
            line.set_label(coefficients.attrs["legend"])
            legend = True
    if legend:
        fig.legend()
    ax1.set_xlabel("α [°]")
    ax1.set_ylabel("lift coefficient")
    ax2.set_xlabel("α [°]")
    ax2.set_ylabel("drag coefficient")
    ax3.set_xlabel("α [°]")
    ax3.set_ylabel("moment coefficient")
    ax4.set_xlabel("α [°]")
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


def plot_lift_distribution(
    lift_distribution_array: list[DataFrame[LiftCoefficientDistribution]],
    label_array: list[str] | None = None,
) -> None:
    """
    Plot the lift coefficient distribution.

    :param lift_distribution: DataFrame containing the lift coefficient distribution.
    :type lift_distribution: DataFrame[LiftCoefficientDistribution]
    """
    fig, ax = plt.subplots()
    fig.suptitle("Lift distribution")
    legend = False
    for lift_distribution in lift_distribution_array:
        (line,) = ax.plot(
            lift_distribution["spanwise_location"], lift_distribution["lift_coefficient"]
        )
        label = None
        if label_array:
            label = label_array.pop(0)
        if "legend" in lift_distribution.attrs:
            if label is not None:
                label += " | " + lift_distribution.attrs["legend"]
            else:
                label = lift_distribution.attrs["legend"]
        if label is not None:
            line.set_label(label)
            legend = True
    if legend:
        ax.legend()
    ax.set_xlabel("spanwise location [m]")
    ax.set_ylabel("lift coefficient")
    plt.show()
