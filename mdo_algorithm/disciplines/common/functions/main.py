"""
This module provides functions to calculate aerodynamics parameters.
"""

from mdo_algorithm.disciplines.common.constants import (
    SEA_LEVEL_TEMPERATURE,
    SEA_LEVEL_PRESSURE,
    TEMPERATURE_LAPSE_RATE,
    MOLAR_GAS_CONSTANT,
    MOLAR_MASS_FOR_DRY_AIR,
    GRAVITATIONAL_ACCELERATION,
    SEA_LEVEL_AIR_DYNAMIC_VISCOSITY,
    SUTHERLAND_CONSTANT,
)


def air_density(altitude: float) -> float:
    """
    Calculate air density at a given altitude using the International Standard Atmosphere (ISA).

    :param altitude: Altitude in meters.
    :type altitude: float

    :return: Air density in kg/m^3.
    :rtype: float

    :raises ValueError: If temperature at altitude is below absolute zero.
    """
    h = altitude
    t0 = SEA_LEVEL_TEMPERATURE
    p0 = SEA_LEVEL_PRESSURE
    r0 = MOLAR_GAS_CONSTANT
    m0 = MOLAR_MASS_FOR_DRY_AIR
    l = TEMPERATURE_LAPSE_RATE
    g = GRAVITATIONAL_ACCELERATION

    r = r0 / m0
    t = t0 - l * h
    if t <= 0:
        raise ValueError("Temperature at altitude is below absolute zero.")
    p = p0 * (1 - l * h / t0) ** (g / (r * l))
    rho = p / (r * t)
    return rho


def air_viscosity(temperature: float) -> float:
    """
    Calculate air dynamic viscosity (Pa*s) using Sutherland's formula.

    :param temperature: Temperature in Celsius.
    :type temperature: float

    :return: Dynamic viscosity in Pa*s.
    :rtype: float
    """
    t = temperature + 273.15
    t0 = SEA_LEVEL_TEMPERATURE
    mu0 = SEA_LEVEL_AIR_DYNAMIC_VISCOSITY
    s = SUTHERLAND_CONSTANT

    mu = mu0 * (t / t0) ** 1.5 * (t0 + s) / (t + s)
    return mu


def reynolds_number(
    velocity: float, reference_length: float, altitude: float, temperature: float
) -> float:
    """
    Calculate the Reynolds number for given flight conditions.

    :param velocity: Velocity of the aircraft (m/s).
    :type velocity: float

    :param reference_length: Chord length of the airfoil (m).
    :type reference_length: float

    :param altitude: Altitude of the flight (m).
    :type altitude: float

    :param temperature: Temperature at altitude (°C).
    :type temperature: float

    :return: Reynolds number (dimensionless).
    :rtype: float
    """
    v = velocity
    l = reference_length
    h = altitude
    t = temperature

    rho = air_density(h)
    mu = air_viscosity(t)

    re = (rho * v * l) / mu
    return re
