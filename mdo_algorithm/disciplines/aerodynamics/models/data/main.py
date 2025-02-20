"""
Aerodynamics data models
"""

import pandera as pa
from pandera.typing import Index, Series


class Coefficients(pa.DataFrameModel):
    """
    DataFrame model for aerodynamic coefficients.
    """

    idx: Index[int]
    alpha: Series[float]
    lift_coefficient: Series[float]
    drag_coefficient: Series[float]
    moment_coefficient: Series[float]
