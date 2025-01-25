from dataclasses import dataclass


@dataclass
class Airfoil:
    name: str


@dataclass
class Wing:
    airfoil: Airfoil
