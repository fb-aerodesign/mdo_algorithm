"""
This script tests the AVL tools
"""

import os

from mdo_algorithm.disciplines.common.models.geometries import Xyz
from mdo_algorithm.disciplines.aerodynamics.constants import AVL_PATH
from mdo_algorithm.disciplines.aerodynamics.models.geometries import (
    Airfoil,
    WingSection,
    Wing,
)
from mdo_algorithm.disciplines.aerodynamics.models import avl

wing = Wing(
    section_array=[
        WingSection(
            location=Xyz(0, 0, 0), chord=0.6, incremental_angle=0, airfoil=Airfoil("s1223")
        ),
        WingSection(
            location=Xyz(0.15, 1.15, 0), chord=0.3, incremental_angle=0, airfoil=Airfoil("s1223")
        ),
    ]
)

avl_input = avl.Input(
    header=avl.Header(
        title="Plane",
        default_mach_number=0,
        y_symmetry=avl.Symmetry.IGNORE,
        z_symmetry=avl.Symmetry.IGNORE,
        xy_plane_location=0,
        reference_area=round(wing.planform_area(), 3),
        reference_chord=round(wing.mean_aerodynamic_chord(), 3),
        reference_span=wing.span(),
        default_location=Xyz(0, 0, 0),
        default_profile_drag_coefficient=None,
    ),
    surface_array=[
        avl.Surface(
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
                avl.Section(
                    location=wing_section.location,
                    chord=wing_section.chord,
                    incremental_angle=wing_section.incremental_angle,
                    spanwise_vortice_count=None,
                    spanwise_vortex_spacing=None,
                    airfoil=wing_section.airfoil,
                    control_array=[],
                    cl_alpha_slope_scaling=None,
                    profile_drag_settings=None,
                )
                for wing_section in wing.section_array
            ],
        )
    ],
    body_array=[],
)

with open(os.path.join(os.getcwd(), AVL_PATH, "input.avl"), "w", encoding="utf-8") as f:
    f.write(avl_input.to_input_file())
