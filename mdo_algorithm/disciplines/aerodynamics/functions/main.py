"""
Aerodynamics functions
"""

from pandera.typing import DataFrame

import numpy as np
from scipy.stats import linregress

from mdo_algorithm.disciplines.aerodynamics.models.xfoil import Coefficients

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
    cl = xfoil_coefficients.loc[mask, "Cl"]

    res = linregress(alpha, cl)

    return res.slope
