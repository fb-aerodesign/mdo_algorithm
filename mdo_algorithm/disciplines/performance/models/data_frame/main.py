"""
Performance data models
"""

import pandera as pa
from pandera.typing import Index, Series


class PropellerBlade(pa.DataFrameModel):
    """
    DataFrame model for propeller blade data.
    """

    idx: Index[int]
    radius: Series[float]
    chord: Series[float]
    beta: Series[float]
    cl_at_alpha_0: Series[float]
    cl_alpha_slope: Series[float]
    cl_min: Series[float]
    cl_max: Series[float]
    cd_at_cl_0: Series[float]
    cl_at_cd_min: Series[float]
    cd_quadratic_upper: Series[float]
    cd_quadratic_lower: Series[float]
    reference_reynolds: Series[float]
    reynolds_expoent: Series[float]
