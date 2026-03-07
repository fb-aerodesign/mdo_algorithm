"""
Get wing area
"""

from rich.console import Console
from rich.table import Table

from utils import config  # pylint: disable=unused-import

from mdo_algorithm.disciplines.common.models.geometries import Point

from mdo_algorithm.disciplines.aerodynamics.models.geometries import (
    Airfoil,
    SurfaceSection,
    Wing,
)


def _build_section_array(cfg: dict, airfoil: Airfoil) -> list[SurfaceSection]:
    """Monta a lista de SurfaceSection conforme a forma da asa (retangular, trapezoidal ou misto)."""
    forma = cfg["forma"]
    b = cfg["b"]
    chord_root = cfg["chord_root"]
    chord_tip = cfg["chord_tip"]
    sweep_x = cfg.get("sweep_x", 0.0)

    match forma:
        case "retangular":
            return [
                SurfaceSection(
                    location=Point(0, 0, 0),
                    chord=chord_root,
                    incremental_angle=0,
                    airfoil=airfoil,
                ),
                SurfaceSection(
                    location=Point(sweep_x, b / 2, 0),
                    chord=chord_root,
                    incremental_angle=0,
                    airfoil=airfoil,
                ),
            ]
        case "trapezoidal":
            return [
                SurfaceSection(
                    location=Point(0, 0, 0),
                    chord=chord_root,
                    incremental_angle=0,
                    airfoil=airfoil,
                ),
                SurfaceSection(
                    location=Point(sweep_x, b / 2, 0),
                    chord=chord_tip,
                    incremental_angle=0,
                    airfoil=airfoil,
                ),
            ]
        case "misto":
            # Seção retangular (raiz até intermediária), depois trapezoidal (até ponta)
            b_rect = cfg["b_rect"]  # meia-envergadura da parte retangular
            sweep_x_rect = cfg.get("sweep_x_rect", 0.0)
            sweep_x_trap = cfg.get("sweep_x_trap", 0.0)
            return [
                SurfaceSection(
                    location=Point(0, 0, 0),
                    chord=chord_root,
                    incremental_angle=0,
                    airfoil=airfoil,
                ),
                SurfaceSection(
                    location=Point(sweep_x_rect, b_rect, 0),
                    chord=chord_root,
                    incremental_angle=0,
                    airfoil=airfoil,
                ),
                SurfaceSection(
                    location=Point(sweep_x_trap, b / 2, 0),
                    chord=chord_tip,
                    incremental_angle=0,
                    airfoil=airfoil,
                ),
            ]
        case _:
            raise ValueError(f"Forma de asa desconhecida: {forma}")


def main():
    """
    Get wing area
    """

    wing_configs = [
        {
            "nome": "2025",
            "forma": "trapezoidal",
            "b": 2.6,
            "chord_root": 0.6,
            "chord_tip": 0.3,
            "sweep_x": 0.15,
            "peso_vazio": 4.8,
        },
        {
            "nome": "2026 retangular 1",
            "forma": "retangular",
            "b": 1.5,
            "chord_root": 0.6,
            "chord_tip": 0.6,
            "sweep_x": 0,
            "peso_vazio": 3,
        },
        {
            "nome": "2026 misto 1",
            "forma": "misto",
            "b": 2,
            "b_rect": 0.5,
            "chord_root": 0.6,
            "chord_tip": 0.25,
            "sweep_x_rect": 0,
            "sweep_x_trap": 0.12,
            "peso_vazio": 3,
        },
    ]

    rho = 1.1
    v = 11.5
    cl = 1.2

    airfoil = Airfoil("s1223")
    wings_array = []
    for cfg in wing_configs:
        section_array = _build_section_array(cfg, airfoil)
        wing = Wing(section_array=section_array)
        area = wing.planform_area()
        lift = 0.5 * rho * v**2 * area * cl
        mtow = lift / 10
        carga_paga = mtow - cfg["peso_vazio"]
        wings_array.append(
            {
                "nome": cfg["nome"],
                "forma": cfg["forma"],
                "envergadura": cfg["b"],
                "area": area,
                "mtow": mtow,
                "peso_vazio": cfg["peso_vazio"],
                "carga_paga": carga_paga,
            }
        )

    table = Table(title="Comparativo de asas")
    table.add_column("Configuração", style="cyan")
    table.add_column("Forma", style="cyan")
    table.add_column("Envergadura (m)", justify="right", style="green")
    table.add_column("Área (m²)", justify="right", style="green")
    table.add_column("MTOW (kg)", justify="right", style="yellow")
    table.add_column("Peso Vazio (kg)", justify="right", style="yellow")
    table.add_column("Carga Paga (kg)", justify="right", style="magenta")

    for w in wings_array:
        table.add_row(
            w["nome"],
            w["forma"],
            f"{w['envergadura']:.2f}",
            f"{w['area']:.2f}",
            f"{w['mtow']:.2f}",
            f"{w['peso_vazio']:.2f}",
            f"{w['carga_paga']:.2f}",
        )

    console = Console()
    console.print(table)


if __name__ == "__main__":
    main()
