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
    CoefficientDistribution,
    ChordwisePressureCoefficient,
)


def _cp_upper_lower_arrays(
    chordwise_pressure_coefficient: DataFrame[ChordwisePressureCoefficient],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Build common x-grid and Cp arrays for upper and lower surfaces.
    """
    leading_edge_idx = int(chordwise_pressure_coefficient["x"].idxmin())
    upper_surface = chordwise_pressure_coefficient.iloc[: leading_edge_idx + 1].copy()
    lower_surface = chordwise_pressure_coefficient.iloc[leading_edge_idx:].copy()

    upper_surface = (
        upper_surface.sort_values("x")
        .groupby("x", as_index=False)
        .mean(numeric_only=True)
    )
    lower_surface = (
        lower_surface.sort_values("x")
        .groupby("x", as_index=False)
        .mean(numeric_only=True)
    )

    x_common = np.union1d(
        upper_surface["x"].to_numpy(),
        lower_surface["x"].to_numpy(),
    )
    cp_upper = np.interp(
        x_common,
        upper_surface["x"].to_numpy(),
        upper_surface["pressure_coefficient"].to_numpy(),
    )
    cp_lower = np.interp(
        x_common,
        lower_surface["x"].to_numpy(),
        lower_surface["pressure_coefficient"].to_numpy(),
    )
    return x_common, cp_upper, cp_lower


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


def center_of_pressure(
    chordwise_pressure_coefficient: DataFrame[ChordwisePressureCoefficient],
) -> tuple[float, float, float]:
    """
    Calculate center of pressure from chordwise pressure data using integration.

    :param chordwise_pressure_coefficient: Chordwise pressure coefficient distribution.
    :type chordwise_pressure_coefficient: DataFrame[ChordwisePressureCoefficient]

    :return:
        Tuple with center of pressure and integrated coefficients:
        - x_cp_over_c: center of pressure position over chord
        - normal_force_coefficient: Cn = integral(delta_cp dx)
        - moment_le_coefficient: Cm_LE = integral(x * delta_cp dx)
    :rtype: tuple[float, float, float]
    """
    x_common, cp_upper, cp_lower = _cp_upper_lower_arrays(chordwise_pressure_coefficient)
    delta_cp = cp_lower - cp_upper
    normal_force_integral = np.trapz(delta_cp, x_common)
    moment_le_integral = np.trapz(x_common * delta_cp, x_common)
    normal_force_coefficient = float(np.asarray(normal_force_integral).item())
    moment_le_coefficient = float(np.asarray(moment_le_integral).item())
    x_cp_over_c = (
        moment_le_coefficient / normal_force_coefficient
        if abs(normal_force_coefficient) > 1e-12
        else float("nan")
    )
    return x_cp_over_c, normal_force_coefficient, moment_le_coefficient


def chordwise_pressure_difference(
    chordwise_pressure_coefficient: DataFrame[ChordwisePressureCoefficient],
) -> tuple[np.ndarray, np.ndarray]:
    """
    Calculate pressure-coefficient difference along chord.

    :param chordwise_pressure_coefficient: Chordwise pressure coefficient distribution.
    :type chordwise_pressure_coefficient: DataFrame[ChordwisePressureCoefficient]

    :return:
        Common x-grid and pressure difference:
        - x_common
        - delta_cp = Cp_lower - Cp_upper
    :rtype: tuple[np.ndarray, np.ndarray]
    """
    x_common, cp_upper, cp_lower = _cp_upper_lower_arrays(chordwise_pressure_coefficient)
    return x_common, cp_lower - cp_upper


def plot_airfoil_pressure_distribution(
    chordwise_pressure_coefficient: DataFrame[ChordwisePressureCoefficient],
    x_cp_over_c: float | None = None,
) -> None:
    """
    Plot airfoil shape and pressure distribution along the chord.

    :param chordwise_pressure_coefficient: Chordwise pressure coefficient distribution.
    :type chordwise_pressure_coefficient: DataFrame[ChordwisePressureCoefficient]

    :param x_cp_over_c: Optional center of pressure location over chord. If not provided,
        it is calculated from the pressure distribution.
    :type x_cp_over_c: float | None
    """
    if x_cp_over_c is None:
        x_cp_over_c, _, _ = center_of_pressure(chordwise_pressure_coefficient)

    x_common, cp_upper, cp_lower = _cp_upper_lower_arrays(chordwise_pressure_coefficient)
    x_profile = chordwise_pressure_coefficient["x"].to_numpy()
    y_profile = chordwise_pressure_coefficient["y"].to_numpy()

    fig, (ax_profile, ax_cp) = plt.subplots(
        2, 1, sharex=True, figsize=(10, 7), gridspec_kw={"height_ratios": [2, 3]}
    )
    fig.suptitle("Airfoil profile, Cp distribution and center of pressure")

    ax_profile.plot(x_profile, y_profile, color="black", linewidth=1.2, label="Airfoil")
    ax_profile.axhline(0, color="gray", linewidth=0.8, linestyle="--")
    ax_profile.axvline(x_cp_over_c, color="red", linewidth=1.2, linestyle="--")
    ax_profile.scatter([x_cp_over_c], [0], color="red", s=30, zorder=3, label="Center of pressure")
    ax_profile.set_ylabel("y/c")
    ax_profile.set_aspect("equal", adjustable="box")
    ax_profile.grid(True, alpha=0.3)
    ax_profile.legend(loc="best")

    ax_cp.plot(x_common, cp_upper, color="tab:blue", linewidth=1.5, label="Cp upper")
    ax_cp.plot(x_common, cp_lower, color="tab:orange", linewidth=1.5, label="Cp lower")
    ax_cp.fill_between(
        x_common,
        cp_lower,
        cp_upper,
        where=(cp_lower >= cp_upper),
        alpha=0.2,
        color="tab:green",
        label="ΔCp",
    )
    ax_cp.axvline(x_cp_over_c, color="red", linewidth=1.2, linestyle="--")
    ax_cp.invert_yaxis()
    ax_cp.set_xlabel("x/c")
    ax_cp.set_ylabel("Cp")
    ax_cp.grid(True, alpha=0.3)
    ax_cp.legend(loc="best")
    plt.tight_layout()
    plt.show()


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
    ax1.set_xlabel("α [°]")
    ax1.set_ylabel("lift coefficient")
    ax1.grid()
    ax2.set_xlabel("α [°]")
    ax2.set_ylabel("drag coefficient")
    ax2.grid()
    ax3.set_xlabel("α [°]")
    ax3.set_ylabel("moment coefficient")
    ax3.grid()
    ax4.set_xlabel("α [°]")
    ax4.set_ylabel("lift coefficient/drag coefficient")
    ax4.grid()
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


def plot_coefficient_distribution(
    coefficient_distribution_array: list[DataFrame[CoefficientDistribution]],
    label_array: list[str] | None = None,
) -> None:
    """
    Plot the coefficient distribution.

    :param coefficient_distribution: DataFrame containing the coefficient distribution.
    :type coefficient_distribution: DataFrame[CoefficientDistribution]
    """
    fig, ax = plt.subplots()
    fig.suptitle("Coefficient distribution")
    legend = False
    for coefficient_distribution in coefficient_distribution_array:
        (line,) = ax.plot(
            coefficient_distribution["spanwise_location"],
            coefficient_distribution["lift_coefficient"],
        )
        label = None
        if label_array:
            label = label_array.pop(0)
        if "legend" in coefficient_distribution.attrs:
            if label is not None:
                label += " | " + coefficient_distribution.attrs["legend"]
            else:
                label = coefficient_distribution.attrs["legend"]
        if label is not None:
            line.set_label(label)
            legend = True
    if legend:
        ax.legend()
    ax.set_xlabel("spanwise location [m]")
    ax.set_ylabel("lift coefficient")
    plt.show()
