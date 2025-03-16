"""
Performance QPROP models
"""

from typing import overload, IO
from dataclasses import dataclass

from pandera.typing import DataFrame

from mdo_algorithm.disciplines.performance.models.data_frame import PropellerBlade


@dataclass
class FluidConstantsInput:
    """
    Fluid constants input for QPROP.

    :param density: Density of the fluid in kg/m³.
    :type density: float

    :param viscosity: Dynamic viscosity of the fluid in kg/(m*s).
    :type viscosity: float

    :param speed_of_sound: Speed of sound in the fluid in m/s.
    :type speed_of_sound: float
    """

    density: float
    viscosity: float
    speed_of_sound: float

    @overload
    def to_def(self) -> str: ...

    @overload
    def to_def(self, file: None = None) -> str: ...

    @overload
    def to_def(self, file: IO[str]) -> None: ...

    def to_def(self, file: IO[str] | None = None) -> str | None:
        """
        Export formatted QPROP file.

        :param file: File to write the fluid constants input to.
        :type file: IO[str] | None
        """
        line_array = [
            "# Fluid Constants",
            "",
            "# Density (kg/m^3)",
            str(float(self.density)),
            "",
            "# Viscosity (kg/(m*s))",
            str(float(self.viscosity)),
            "",
            "# Speed of Sound (m/s)",
            str(float(self.speed_of_sound)),
            "",
        ]
        output = "\n".join(line_array)
        if file is not None:
            file.write(output)
            return None
        return output


@dataclass
class PropellerInput:
    """
    Propeller input for QPROP.
    """

    name: str
    blade_count: int
    reference_radius: float | None
    cl_at_alpha_0: float
    cl_alpha_slope: float
    cl_min: float
    cl_max: float
    cd_at_cl_0: float
    cl_at_cd_min: float
    cd_quadratic_upper: float
    cd_quadratic_lower: float
    reference_reynolds: float
    reynolds_expoent: float
    radius_scaling_factor: float
    chord_scaling_factor: float
    beta_scaling_factor: float
    radius_added: float
    chord_added: float
    beta_added: float
    propeller_blade: DataFrame[PropellerBlade]
