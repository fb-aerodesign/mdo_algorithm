"""
Aerodynamics AVL models

This module defines data structures for configuring aerodynamic models in AVL.
It provides classes to represent key AVL input parameters.
"""

from dataclasses import dataclass, field
from enum import IntEnum
from typing import overload, IO

from pandera.typing import DataFrame
import numpy as np

from mdo_algorithm.disciplines.common.models.geometries import (
    Xyz,
    MassProperties,
)
from mdo_algorithm.disciplines.aerodynamics.functions import cl_alpha_slope
from mdo_algorithm.disciplines.aerodynamics.models.geometries import (
    Airfoil,
    Wing,
)
from mdo_algorithm.disciplines.aerodynamics.models.dataframe import Coefficients


class Symmetry(IntEnum):
    """
    Symmetry type for aerodynamic configurations.

    This class corresponds to the iYsym and iZsym parameters in AVL, which define
    symmetry conditions for the aerodynamic model.

    - SYMMETRIC: Indicates symmetry about the reference plane (1 in AVL).
    - ANTISYMMETRIC: Indicates antisymmetry about the reference plane (-1 in AVL).
    - IGNORE: No symmetry is assumed (0 in AVL).
    """

    SYMMETRIC = 1
    ANTISYMMETRIC = -1
    IGNORE = 0


class Deflection(IntEnum):
    """
    Control deflection direction.

    This class corresponds to the SgnDup parameter in AVL, which specifies whether the
    control deflection is normal or inverted on mirrored surfaces.

    - NORMAL: Control moves in the standard direction (1 in AVL).
    - INVERSE: Control moves in the opposite direction (-1 in AVL).
    """

    NORMAL = 1
    INVERSE = -1


@dataclass
class Header:
    """
    Header information of an AVL input file.

    :param title: Title of the AVL case.
    :type title: str

    :param default_mach_number: Default freestream Mach number.
    :type default_mach_number: float

    :param y_symmetry: Symmetry condition in the Y-plane (corresponds to iYsym in AVL).
    :type y_symmetry: Symmetry

    :param z_symmetry: Symmetry condition in the Z-plane (corresponds to iZsym in AVL).
    :type z_symmetry: Symmetry

    :param xy_plane_location: Reference location for the XY plane (corresponds to Zsym in
    AVL, ignored if z_symmetry/iZsym is IGNORE/0).
    :type xy_plane_location: float

    :param reference_area: Reference wing area (corresponds to Sref in AVL).
    :type reference_area: float

    :param reference_chord: Reference chord length (corresponds to Cref in AVL).
    :type reference_chord: float

    :param reference_span: Reference wingspan (corresponds to Bref in AVL).
    :type reference_span: float

    :param default_location: Default moment reference point (corresponds to Xref, Yref,
    Zref in AVL).
    :type default_location: Xyz

    :param default_profile_drag_coefficient: Default profile drag coefficient
    (corresponds to CDp in AVL).
    :type default_profile_drag_coefficient: float
    """

    title: str
    default_mach_number: float
    y_symmetry: Symmetry
    z_symmetry: Symmetry
    xy_plane_location: float
    reference_area: float
    reference_chord: float
    reference_span: float
    default_location: Xyz
    default_profile_drag_coefficient: float | None

    def to_input_file(self) -> str:
        """
        Export formatted string for the AVL input file
        """
        line_array: list[str] = [
            "# case title",
            self.title,
            "",
            "# Mach",
            str(float(self.default_mach_number)),
            "",
            "# iYsym iZsym Zsym",
            " ".join(
                [
                    str(self.y_symmetry.value),
                    str(self.z_symmetry.value),
                    str(float(self.xy_plane_location)),
                ]
            ),
            "",
            "# Sref Cref Bref",
            " ".join(
                [
                    str(float(self.reference_area)),
                    str(float(self.reference_chord)),
                    str(float(self.reference_span)),
                ]
            ),
            "",
            "# Xref Yref Zref",
            " ".join(
                [
                    str(float(self.default_location.x)),
                    str(float(self.default_location.y)),
                    str(float(self.default_location.z)),
                ]
            ),
        ]
        if self.default_profile_drag_coefficient is not None:
            line_array.extend(["", "# CDp", str(float(self.default_profile_drag_coefficient)), ""])
        if line_array[-1] != "":
            line_array.append("")
        return "\n".join(line_array)


@dataclass
class ProfileDragSettings:
    """
    Profile drag characteristics as a function of lift coefficient.

    This class corresponds to the CDCL keyword in AVL.

    :param cl1: Lift coefficient at the first drag breakpoint.
    :type cl1: float

    :param cd1: Drag coefficient corresponding to cl1.
    :type cd1: float

    :param cl2: Lift coefficient at the second drag breakpoint.
    :type cl2: float

    :param cd2: Drag coefficient corresponding to cl2.
    :type cd2: float

    :param cl3: Lift coefficient at the third drag breakpoint.
    :type cl3: float

    :param cd3: Drag coefficient corresponding to cl3.
    :type cd3: float
    """

    cl1: float
    cd1: float
    cl2: float
    cd2: float
    cl3: float
    cd3: float

    @staticmethod
    def from_xfoil_coefficients(coefficients: DataFrame[Coefficients]) -> "ProfileDragSettings":
        """
        Create profile drag settings from XFOIL coefficients.

        :param coefficients: XFOIL coefficients for the airfoil.
        :type coefficients: DataFrame[Coefficients]

        :return: Profile drag settings based on the coefficients.
        :rtype: ProfileDragSettings
        """
        return ProfileDragSettings(
            cl1=float(coefficients["lift_coefficient"].min()),
            cd1=float(
                coefficients.at[coefficients["lift_coefficient"].idxmin(), "drag_coefficient"]
            ),
            cl2=float(coefficients.loc[coefficients["alpha"] == 0, "lift_coefficient"].values[0]),
            cd2=float(coefficients.loc[coefficients["alpha"] == 0, "drag_coefficient"].values[0]),
            cl3=float(coefficients["lift_coefficient"].max()),
            cd3=float(
                coefficients.at[coefficients["lift_coefficient"].idxmax(), "drag_coefficient"]
            ),
        )


@dataclass
class Control:
    """
    Control surface definition in AVL.

    :param name: Name of the control surface.
    :type name: str

    :param gain: Gain factor as deflection per unit control input (corresponds to gain
    in AVL).
    :type gain: float

    :param hinge_x_location: Position of the hinge along the chord (corresponds to Xhinge
    in AVL).
    :type hinge_x_location: float

    :param hinge_axis_location: Axis of rotation for the control surface (corresponds
    to XYZhvec in AVL).
    :type hinge_axis_location: Xyz

    :param deflection: Direction of control deflection (corresponds to SgnDup in AVL).
    :type deflection: Deflection
    """

    name: str
    gain: float
    hinge_x_location: float
    hinge_axis_location: Xyz
    deflection: Deflection

    def to_input_file(self) -> str:
        """
        Export formatted string for the AVL input file
        """
        line_array: list[str] = [
            "CONTROL",
            "",
            "# name, gain, Xhinge, XYZhvec, SgnDup",
            " ".join(
                [
                    self.name,
                    str(float(self.gain)),
                    str(float(self.hinge_x_location)),
                    str(float(self.hinge_axis_location.x)),
                    str(float(self.hinge_axis_location.y)),
                    str(float(self.hinge_axis_location.z)),
                    str(self.deflection.value),
                ]
            ),
            "",
        ]
        return "\n".join(line_array)


@dataclass
class Section:
    """
    Sectional element of a surface in AVL.

    :param location: Position of the leading edge (corresponds to Xle, Yle
    and Zle in AVL).
    :type location: Xyz

    :param chord: Section chord length (corresponds to Chord in AVL).
    :type chord: float

    :param incremental_angle: Additional incidence angle (corresponds to Ainc in AVL).
    :type incremental_angle: float

    :param spanwise_vortice_count: Number of spanwise vortices (corresponds to Nspan
    in AVL).
    :type spanwise_vortice_count: int | None

    :param spanwise_vortex_spacing: Spanwise vortex spacing (corresponds to Sspace in
    AVL).
    :type spanwise_vortex_spacing: float | None

    :param airfoil: Airfoil profile of the section.
    :type airfoil: Airfoil

    :param control_array: List of associated control surfaces.
    :type control_array: list["Control"]

    :param cl_alpha_slope_scaling: Scaling factor for lift slope (corresponds to the
    CLAF keyword in AVL as dCL/da scaling factor).
    :type cl_alpha_slope_scaling: float | None

    :param profile_drag_settings: Drag settings for this section (corresponds to the
    CDCL keyword in AVL as CL1, CD1, CL2, CD2, CL3, CD3).
    :type profile_drag_settings: ProfileDragSettings | None
    """

    location: Xyz
    chord: float
    incremental_angle: float
    spanwise_vortice_count: int | None
    spanwise_vortex_spacing: float | None
    airfoil: Airfoil
    control_array: list[Control]
    cl_alpha_slope_scaling: float | None
    profile_drag_settings: ProfileDragSettings | None

    def to_input_file(self) -> str:
        """
        Export formatted string for the AVL input file
        """
        line_array: list[str] = [
            "SECTION",
            "",
            "# Xle Yle Zle Chord Ainc [ Nspan Sspace ]",
            " ".join(
                [
                    str(float(self.location.x)),
                    str(float(self.location.y)),
                    str(float(self.location.z)),
                    str(float(self.chord)),
                    str(float(self.incremental_angle)),
                    (
                        str(self.spanwise_vortice_count)
                        if self.spanwise_vortice_count is not None
                        else ""
                    ),
                    (
                        str(float(self.spanwise_vortex_spacing))
                        if self.spanwise_vortex_spacing is not None
                        else ""
                    ),
                ]
            ),
            "",
            "# airfoil",
            "AFILE",
            self.airfoil.relative_path(),
        ]
        if self.cl_alpha_slope_scaling is not None:
            line_array.extend(
                [
                    "",
                    "# dCL/da scaling factor",
                    "CLAF",
                    str(float(self.cl_alpha_slope_scaling)),
                    "",
                ]
            )
        if self.profile_drag_settings is not None:
            line_array.extend(
                [
                    "# CD (CL) function parameters",
                    "CDCL",
                    "",
                    "# CL1 CD1 CL2 CD2 CL3 CD3",
                    " ".join(
                        [
                            str(float(self.profile_drag_settings.cl1)),
                            str(float(self.profile_drag_settings.cd1)),
                            str(float(self.profile_drag_settings.cl2)),
                            str(float(self.profile_drag_settings.cd2)),
                            str(float(self.profile_drag_settings.cl3)),
                            str(float(self.profile_drag_settings.cd3)),
                        ]
                    ),
                    "",
                ]
            )
        if line_array[-1] != "":
            line_array.append("")
        return "\n".join(line_array) + "\n".join(
            [control.to_input_file() for control in self.control_array]
        )


@dataclass
class Body:
    """
    Fuselage or other non-lifting body in AVL.

    :param name: Name of the body.
    :type name: str

    :param node_count: Number of source-line nodes (corresponds to Nbody in AVL).
    :type node_count: int

    :param node_spacing: Spacing distribution of nodes (corresponds to Bspace in AVL).
    :type node_spacing: float

    :param mirror_surface: Whether the body is mirrored (corresponds to the YDUPLICATE
    keyword in AVL).
    :type mirror_surface: bool

    :param xz_plane_location: Reference location for mirroring (corresponds to Ydupl
    in AVL, required if mirror_surface is True).
    :type xz_plane_location: float | None

    :param scale: Scaling factors in X, Y, and Z directions (corresponds to the
    SCALE keyword in AVL as Xscale, Yscale and Zscale).
    :type scale: Xyz | None

    :param translate: Translation vector (corresponds to the TRANSLATE keyword in AVL
    as dX, dY and dZ).
    :type translate: Xyz | None
    """

    name: str
    node_count: int
    node_spacing: float
    mirror_surface: bool
    xz_plane_location: float | None
    scale: Xyz | None
    translate: Xyz | None

    def to_input_file(self) -> str:
        """
        Export formatted string for the AVL input file
        """
        line_array: list[str] = [
            "BODY",
            "",
            "# body name string",
            self.name,
            "",
            "# Nbody Bspace",
            " ".join([str(self.node_count), str(float(self.node_spacing))]),
        ]
        if self.mirror_surface:
            if self.xz_plane_location is None:
                raise ValueError("XY plane location must be defined if mirror surface is True")
            line_array.extend(
                [
                    "",
                    "YDUPLICATE",
                    "",
                    "# Ydupl",
                    str(float(self.xz_plane_location)),
                    "",
                ]
            )
        if self.scale is not None:
            line_array.extend(
                [
                    "",
                    "SCALE",
                    "",
                    "# Xscale Yscale Zscale",
                    " ".join(
                        [
                            str(float(self.scale.x)),
                            str(float(self.scale.y)),
                            str(float(self.scale.z)),
                        ]
                    ),
                    "",
                ]
            )
        if self.translate is not None:
            line_array.extend(
                [
                    "",
                    "TRANSLATE",
                    "",
                    "# dX dY dZ",
                    " ".join(
                        [
                            str(float(self.translate.x)),
                            str(float(self.translate.y)),
                            str(float(self.translate.z)),
                        ]
                    ),
                    "",
                ]
            )
        if line_array[-1] != "":
            line_array.append("")
        return "\n".join(line_array)


@dataclass
class Surface:
    """
    Defines a lifting surface in AVL.

    :param name: Name of the surface.
    :type name: str

    :param chordwise_vortice_count: Number of chordwise vortices (corresponds to Nchord
    in AVL).
    :type chordwise_vortice_count: int

    :param chordwise_vortex_spacing: Chordwise vortex spacing (corresponds to Cspace
    in AVL).
    :type chordwise_vortex_spacing: float

    :param spanwise_vortice_count: Number of spanwise vortices (corresponds to Nspan
    in AVL).
    :type spanwise_vortice_count: int | None

    :param spanwise_vortex_spacing: Spanwise vortex spacing (corresponds to Sspace
    in AVL).
    :type spanwise_vortex_spacing: float | None

    :param mirror_surface: Whether the surface is mirrored (corresponds to the YDUPLICATE
    keyword in AVL).
    :type mirror_surface: bool

    :param xz_plane_location: Reference location for mirroring (corresponds to Ydupl
    in AVL, required if mirror_surface is True).
    :type xz_plane_location: float | None

    :param scale: Scaling factors in X, Y, and Z directions (corresponds to the SCALE
    keyword in AVL as Xscale, Yscale and Zscale).
    :type scale: Xyz | None

    :param translate: Translation vector (corresponds to the TRANSLATE keyword in AVL
    as dX, dY and dZ).
    :type translate: Xyz | None

    :param incremental_angle: Additional incidence angle (corresponds to the ANGLE keyword
    in AVL as dAinc).
    :type incremental_angle: float | None

    :param ignore_wake: Whether wake generation is disabled (corresponds to the NOWAKE
    keyword in AVL).
    :type ignore_wake: bool

    :param ignore_freestream_effect: Whether freestream influence is ignored (corresponds
    to the NOALBE keyword in AVL).
    :type ignore_freestream_effect: bool

    :param ignore_load_contribution: Whether surface loads are excluded from total forces
    (corresponds to the NOLOAD keyword in AVL).
    :type ignore_load_contribution: bool

    :param profile_drag_settings: Profile drag settings (corresponds to the CDCL keyword
    in AVL as CL1, CD1, CL2, CD2, CL3, CD3).
    :type profile_drag_settings: ProfileDragSettings | None

    :param section_array: List of sectional elements defining the surface.
    :type section_array: list[Section]
    """

    name: str
    chordwise_vortice_count: int
    chordwise_vortex_spacing: float
    spanwise_vortice_count: int | None
    spanwise_vortex_spacing: float | None
    mirror_surface: bool
    xz_plane_location: float | None
    scale: Xyz | None
    translate: Xyz | None
    incremental_angle: float | None
    ignore_wake: bool
    ignore_freestream_effect: bool
    ignore_load_contribution: bool
    profile_drag_settings: ProfileDragSettings | None
    section_array: list[Section]

    def to_input_file(self) -> str:
        """
        Export formatted string for the AVL input file
        """
        line_array: list[str] = [
            "SURFACE",
            "",
            "# surface name string",
            self.name,
            "",
            "# Nchord Cspace [ Nspan Sspace ]",
            " ".join(
                [
                    str(self.chordwise_vortice_count),
                    str(float(self.chordwise_vortex_spacing)),
                    (
                        str(self.spanwise_vortice_count)
                        if self.spanwise_vortice_count is not None
                        else ""
                    ),
                    (
                        str(float(self.spanwise_vortex_spacing))
                        if self.spanwise_vortex_spacing is not None
                        else ""
                    ),
                ]
            ),
        ]
        if self.mirror_surface:
            if self.xz_plane_location is None:
                raise ValueError("XY plane location must be defined if mirror surface is True")
            line_array.extend(
                [
                    "",
                    "YDUPLICATE",
                    "",
                    "# Ydupl",
                    str(float(self.xz_plane_location)),
                    "",
                ]
            )
        if self.scale is not None:
            line_array.extend(
                [
                    "",
                    "SCALE",
                    "",
                    "# Xscale Yscale Zscale",
                    " ".join(
                        [
                            str(float(self.scale.x)),
                            str(float(self.scale.y)),
                            str(float(self.scale.z)),
                        ]
                    ),
                    "",
                ]
            )
        if self.translate is not None:
            line_array.extend(
                [
                    "",
                    "TRANSLATE",
                    "",
                    "# dX dY dZ",
                    " ".join(
                        [
                            str(float(self.translate.x)),
                            str(float(self.translate.y)),
                            str(float(self.translate.z)),
                        ]
                    ),
                    "",
                ]
            )
        if self.incremental_angle is not None:
            line_array.extend(
                [
                    "",
                    "ANGLE",
                    "",
                    "# dAinc",
                    str(float(self.incremental_angle)),
                    "",
                ]
            )
        if self.ignore_wake:
            line_array.extend(["NOWAKE", ""])
        if self.ignore_freestream_effect:
            line_array.extend(["NOALBE", ""])
        if self.ignore_load_contribution:
            line_array.extend(["NOLOAD", ""])
        if self.profile_drag_settings is not None:
            line_array.extend(
                [
                    "",
                    "# CD (CL) function parameters",
                    "CDCL",
                    "",
                    "# CL1 CD1 CL2 CD2 CL3 CD3",
                    " ".join(
                        [
                            str(float(self.profile_drag_settings.cl1)),
                            str(float(self.profile_drag_settings.cd1)),
                            str(float(self.profile_drag_settings.cl2)),
                            str(float(self.profile_drag_settings.cd2)),
                            str(float(self.profile_drag_settings.cl3)),
                            str(float(self.profile_drag_settings.cd3)),
                        ]
                    ),
                    "",
                ]
            )
        if line_array[-1] != "":
            line_array.append("")
        return "\n".join(
            [
                "\n".join(line_array),
                "\n".join([section.to_input_file() for section in self.section_array]),
            ]
        )


@dataclass
class GeometryInput:
    """
    AVL geometry input configuration.

    :param header: Header information of the AVL input file.
    :type header: Header

    :param surface_array: List of defined lifting surfaces.
    :type surface_array: list[Surface]

    :param body_array: List of defined fuselage bodies.
    :type body_array: list[Body]
    """

    header: Header
    surface_array: list[Surface]
    body_array: list[Body]

    @staticmethod
    def from_wing(
        wing: Wing,
        xfoil_coefficients_array: list[DataFrame[Coefficients]] | None = None,
    ) -> "GeometryInput":
        """
        Create AVL geometry input from a Wing object.

        :param wing: Wing object to convert to AVL geometry input.
        :type wing: Wing

        :param xfoil_coefficients_array: Array of XFOIL coefficients for each section.
        :type xfoil_coefficients_array: list[DataFrame[Coefficients]] | None

        :return: AVL geometry input corresponding to the wing.
        :rtype: GeometryInput
        """
        if xfoil_coefficients_array is not None and len(wing.section_array) != len(
            xfoil_coefficients_array
        ):
            raise ValueError(
                "The number of wing sections must be equal to the number of XFOIL coefficients"
            )
        return GeometryInput(
            header=Header(
                title="Plane",
                default_mach_number=0,
                y_symmetry=Symmetry.IGNORE,
                z_symmetry=Symmetry.IGNORE,
                xy_plane_location=0,
                reference_area=round(wing.planform_area(), 3),
                reference_chord=round(wing.mean_aerodynamic_chord(), 3),
                reference_span=wing.span(),
                default_location=Xyz(0.25 * wing.section_array[0].chord, 0, 0),
                default_profile_drag_coefficient=None,
            ),
            surface_array=[
                Surface(
                    name="Wing",
                    chordwise_vortice_count=12,
                    chordwise_vortex_spacing=1,
                    spanwise_vortice_count=20,
                    spanwise_vortex_spacing=-1.5,
                    mirror_surface=True,
                    xz_plane_location=0,
                    scale=None,
                    translate=None,
                    incremental_angle=None,
                    ignore_wake=False,
                    ignore_freestream_effect=False,
                    ignore_load_contribution=False,
                    profile_drag_settings=None,
                    section_array=[
                        Section(
                            location=wing_section.location,
                            chord=wing_section.chord,
                            incremental_angle=wing_section.incremental_angle,
                            spanwise_vortice_count=None,
                            spanwise_vortex_spacing=None,
                            airfoil=wing_section.airfoil,
                            control_array=[],
                            cl_alpha_slope_scaling=(
                                round(cl_alpha_slope(xfoil_coefficients_array[i]) / (2 * np.pi), 3)
                                if xfoil_coefficients_array is not None
                                else None
                            ),
                            profile_drag_settings=(
                                ProfileDragSettings.from_xfoil_coefficients(
                                    xfoil_coefficients_array[i]
                                )
                                if xfoil_coefficients_array is not None
                                else None
                            ),
                        )
                        for i, wing_section in enumerate(wing.section_array)
                    ],
                )
            ],
            body_array=[],
        )

    @overload
    def to_avl(self) -> str: ...

    @overload
    def to_avl(self, file: None) -> str: ...

    @overload
    def to_avl(self, file: IO[str]) -> None: ...

    def to_avl(self, file: IO[str] | None = None) -> str | None:
        """
        Export formatted AVL file

        :param file: File to write the AVL input to.
        :type file: IO[str] | None
        """
        avl = "\n".join(
            [
                self.header.to_input_file(),
                "\n".join([surface.to_input_file() for surface in self.surface_array]),
                "\n".join([body.to_input_file() for body in self.body_array]),
            ]
        )
        if file is not None:
            file.write(avl)
            return None
        return avl


@dataclass
class MassInput:
    """
    Mass input for AVL.

    :param length_unit_meters: Length unit in meters.
    :type length_unit_meters: float

    :param mass_unit_kilograms: Mass unit in kilograms.
    :type mass_unit_kilograms: float

    :param time_unit_seconds: Time unit in seconds.
    :type time_unit_seconds: float

    :param gravitational_acceleration: Gravitational acceleration.
    :type gravitational_acceleration: float | None

    :param air_density: Air density in kg/m^3.
    :type air_density: float | None

    :param mass_properties_array: List of mass properties for each component.
    :type mass_properties_array: list[MassProperties]
    """

    length_unit_meters: float = 1
    mass_unit_kilograms: float = 1
    time_unit_seconds: float = 1
    gravitational_acceleration: float | None = None
    air_density: float | None = None
    mass_properties_array: list[MassProperties] = field(default_factory=list)

    @staticmethod
    def from_wing(
        wing: Wing,
        length_unit_meters: float = 1,
        mass_unit_kilograms: float = 1,
        time_unit_seconds: float = 1,
        gravitational_acceleration: float | None = None,
        air_density: float | None = None,
    ) -> "MassInput":
        """
        Create mass input from a Wing object.

        :param wing: Wing object to convert to mass input.
        :type wing: Wing

        :param length_unit_meters: Length unit in meters.
        :type length_unit_meters: float

        :param mass_unit_kilograms: Mass unit in kilograms.
        :type mass_unit_kilograms: float

        :param time_unit_seconds: Time unit in seconds.
        :type time_unit_seconds: float

        :param gravitational_acceleration: Gravitational acceleration.
        :type gravitational_acceleration: float | None

        :param air_density: Air density in kg/m^3.
        :type air_density: float | None

        :return: Mass input corresponding to the wing.
        :rtype: MassInput
        """
        return MassInput(
            length_unit_meters=length_unit_meters,
            mass_unit_kilograms=mass_unit_kilograms,
            time_unit_seconds=time_unit_seconds,
            gravitational_acceleration=gravitational_acceleration,
            air_density=air_density,
            mass_properties_array=[wing.mass_properties],
        )

    @overload
    def to_mass(self) -> str: ...

    @overload
    def to_mass(self, file: None) -> str: ...

    @overload
    def to_mass(self, file: IO[str]) -> None: ...

    def to_mass(self, file: IO[str] | None = None) -> str | None:
        """
        Export formatted AVL file

        :param file: File to write the AVL input to.
        :type file: IO[str] | None
        """
        line_array = [
            "# length unit in meters",
            f"Lunit = {float(self.length_unit_meters)} m",
            "",
            "# mass unit in kilograms",
            f"Munit = {float(self.mass_unit_kilograms)} kg",
            "",
            "# time unit in seconds",
            f"Tunit = {float(self.time_unit_seconds)} s",
            "",
        ]
        if self.gravitational_acceleration is not None:
            line_array.extend(
                [
                    "# gravitational acceleration",
                    f"g = {round(self.gravitational_acceleration, 3)}",
                    "",
                ]
            )
        if self.air_density is not None:
            line_array.extend(
                [
                    "# air density",
                    f"rho = {round(self.air_density, 3)}",
                    "",
                ]
            )
        headers = ["# mass", "Xcg", "Ycg", "Zcg", "Ixx", "Iyy", "Izz", "Ixy", "Ixz", "Iyz"]
        data = [
            [
                float(mass.mass),
                float(mass.center_of_gravity.x),
                float(mass.center_of_gravity.y),
                float(mass.center_of_gravity.z),
                float(mass.moments_of_inertia.x),
                float(mass.moments_of_inertia.y),
                float(mass.moments_of_inertia.z),
                float(mass.products_of_inertia.xy),
                float(mass.products_of_inertia.xz),
                float(mass.products_of_inertia.yz),
            ]
            for mass in self.mass_properties_array
        ]
        col_widths = [max(len(str(item)) for item in col) for col in zip(headers, *data)]
        col_widths[1:] = [v + 2 for v in col_widths[1:]]
        line_array.extend(
            [
                " ".join([f"{header:>{col_widths[i]}}" for i, header in enumerate(headers)]),
                *[
                    " ".join([f"{str(item):>{col_widths[i]}}" for i, item in enumerate(row)])
                    for row in data
                ],
            ]
        )
        output = "\n".join(line_array)
        if file is not None:
            file.write(output)
            return None
        return output
