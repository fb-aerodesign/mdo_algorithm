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


class CoefficientDistribution(pa.DataFrameModel):
    """
    DataFrame model for coefficient distribution.
    """

    idx: Index[int]
    spanwise_location: Series[float]
    lift_coefficient: Series[float]
    moment_coefficient: Series[float]


class ChordwisePressureCoefficient(pa.DataFrameModel):
    """
    DataFrame model for chordwise pressure coefficient.
    """
    idx: Index[int]
    x: Series[float]
    y: Series[float]
    pressure_coefficient: Series[float]
