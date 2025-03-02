"""
Common geometry models
"""

from dataclasses import dataclass, field


@dataclass
class Point:
    """
    Three-dimensional point
    """

    x: float = 0
    y: float = 0
    z: float = 0


@dataclass
class ProductsOfInertia:
    """
    Product of inertia
    """

    xy: float = 0
    xz: float = 0
    yz: float = 0


@dataclass
class MassProperties:
    """
    Mass properties
    """

    mass: float = 0
    center_of_gravity: Point = field(default_factory=Point)
    moments_of_inertia: Point = field(default_factory=Point)
    products_of_inertia: ProductsOfInertia = field(default_factory=ProductsOfInertia)
