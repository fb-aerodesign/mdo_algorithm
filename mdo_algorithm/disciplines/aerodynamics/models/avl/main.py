"""
Aerodynamics AVL models

This module defines data structures for configuring aerodynamic models in AVL.
It provides classes to represent key AVL input parameters.
"""

from dataclasses import dataclass
from enum import IntEnum

from mdo_algorithm.disciplines.common.models.geometries import Xyz
from mdo_algorithm.disciplines.aerodynamics.models.geometries import Airfoil


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
        max_first_value = 2 + max(
            len(v)
            for v in [
                str(self.default_mach_number),
                str(self.reference_area),
                str(self.default_location.x),
                str(self.default_profile_drag_coefficient),
            ]
        )
        max_second_value = 2 + max(
            len(v) for v in [str(self.reference_chord), str(self.default_location.y)]
        )
        data: list[tuple[str, str]] = [
            (self.title, "case title"),
            ("", ""),
            (str(self.default_mach_number).ljust(max_first_value), "Mach"),
            (
                str(self.y_symmetry.value).ljust(max_first_value)
                + str(self.z_symmetry.value).ljust(max_second_value)
                + str(self.xy_plane_location),
                "iYsym  iZsym  Zsym",
            ),
            (
                str(self.reference_area).ljust(max_first_value)
                + str(self.reference_chord).ljust(max_second_value)
                + str(self.reference_span),
                "Sref   Cref   Bref",
            ),
            (
                str(self.default_location.x).ljust(max_first_value)
                + str(self.default_location.y).ljust(max_second_value)
                + str(self.default_location.z),
                "Xref   Yref   Zref",
            ),
        ]
        if self.default_profile_drag_coefficient is not None:
            data.append((str(self.default_profile_drag_coefficient), "CDp"))
        data.append(("", ""))
        max_item_size = 1 + max(len(item) for item, _ in data)
        return "\n".join(
            [
                " | ".join([item.ljust(max_item_size), comment]) if comment != "" else item
                for item, comment in data
            ]
        )


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
        data: list[tuple[str, str]] = [
            (8 * " " + "CONTROL", "(keyword)"),
            (
                8 * " "
                + "  ".join(
                    [
                        self.name,
                        str(self.gain),
                        str(self.hinge_x_location),
                        str(self.hinge_axis_location.x),
                        str(self.hinge_axis_location.y),
                        str(self.hinge_axis_location.z),
                        str(self.deflection.value),
                    ]
                ),
                "name, gain, Xhinge, XYZhvec, SgnDup",
            ),
        ]
        data.append(("", ""))
        max_item_size = 1 + max(len(item) for item, _ in data)
        return "\n".join(
            [
                " | ".join([item.ljust(max_item_size), comment]) if comment != "" else item
                for item, comment in data
            ]
        )


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
        data: list[tuple[str, str]] = [
            (4 * " " + "SECTION", "(keyword)"),
            (
                4 * " "
                + "  ".join(
                    [
                        str(self.location.x),
                        str(self.location.y),
                        str(self.location.z),
                        str(self.chord),
                        str(self.incremental_angle),
                        (
                            str(self.spanwise_vortice_count)
                            if self.spanwise_vortice_count is not None
                            else ""
                        ),
                        (
                            str(self.spanwise_vortex_spacing)
                            if self.spanwise_vortex_spacing is not None
                            else ""
                        ),
                    ]
                ),
                "Xle Yle Zle Chord Ainc [ Nspan Sspace ]",
            ),
            (8 * " " + "AFILE", "(keyword)"),
            (8 * " " + self.airfoil.relative_path(), "filename string"),
        ]
        if self.cl_alpha_slope_scaling is not None:
            data.extend(
                [
                    (8 * " " + "CLAF", "(keyword)"),
                    (8 * " " + str(self.cl_alpha_slope_scaling), "dCL/da scaling factor"),
                ]
            )
        if self.profile_drag_settings is not None:
            data.extend(
                [
                    (8 * " " + "CDCL", "(keyword)"),
                    (
                        8 * " "
                        + "  ".join(
                            [
                                str(self.profile_drag_settings.cl1),
                                str(self.profile_drag_settings.cd1),
                                str(self.profile_drag_settings.cl2),
                                str(self.profile_drag_settings.cd2),
                                str(self.profile_drag_settings.cl3),
                                str(self.profile_drag_settings.cd3),
                            ]
                        ),
                        "CD (CL) function parameters",
                    ),
                ]
            )
        data.append(("", ""))
        max_item_size = 1 + max(len(item) for item, _ in data)
        return (
            "\n".join(
                [
                    " | ".join([item.ljust(max_item_size), comment]) if comment != "" else item
                    for item, comment in data
                ]
            )
            + "\n"
            + "\n".join([control.to_input_file() for control in self.control_array])
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
        data: list[tuple[str, str]] = [
            ("BODY", "(keyword)"),
            (self.name, "body name string"),
            (
                "  ".join(
                    [
                        str(self.node_count),
                        str(self.node_spacing),
                    ]
                ),
                "Nbody Bspace",
            ),
        ]
        if self.mirror_surface:
            if self.xz_plane_location is None:
                raise RuntimeError("XY plane location must be defined if mirror surface is True")
            data.extend(
                [
                    (4 * " " + "YDUPLICATE", "(keyword)"),
                    (4 * " " + str(self.xz_plane_location), "Ydupl"),
                ]
            )
        if self.scale is not None:
            data.extend(
                [
                    (4 * " " + "SCALE", "(keyword)"),
                    (
                        4 * " "
                        + "  ".join(
                            [
                                str(self.scale.x),
                                str(self.scale.y),
                                str(self.scale.z),
                            ]
                        ),
                        "Xscale Yscale Zscale",
                    ),
                ]
            )
        if self.translate is not None:
            data.extend(
                [
                    (4 * " " + "TRANSLATE", "(keyword)"),
                    (
                        4 * " "
                        + "  ".join(
                            [
                                str(self.translate.x),
                                str(self.translate.y),
                                str(self.translate.z),
                            ]
                        ),
                        "dX     dY     dZ",
                    ),
                ]
            )
        data.append(("", ""))
        max_item_size = 1 + max(len(item) for item, _ in data)
        return "\n".join(
            [
                " | ".join([item.ljust(max_item_size), comment]) if comment != "" else item
                for item, comment in data
            ]
        )


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


@dataclass
class Input:
    """
    AVL input configuration.

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
