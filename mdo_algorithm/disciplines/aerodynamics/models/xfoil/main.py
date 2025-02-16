"""
Aerodynamics XFOIL models
"""

import pandera as pa
from pandera.typing import Index, Series


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
