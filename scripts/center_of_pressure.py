"""
Get chordwise pressure coefficient (Cp) for 2D airfoil.
"""

import matplotlib.pyplot as plt
from pandera.typing import DataFrame
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from utils import config  # pylint: disable=unused-import

from mdo_algorithm.disciplines.aerodynamics.models.geometries import Airfoil
from mdo_algorithm.disciplines.aerodynamics.models.data_frame import ChordwisePressureCoefficient
from mdo_algorithm.disciplines.aerodynamics.services.xfoil import XfoilService
from mdo_algorithm.disciplines.aerodynamics.functions import (
    center_of_pressure,
    chordwise_pressure_difference,
)


def main():
    """
    Get center of pressure for multiple angles via XFOIL CPWR.
    """
    airfoil_name = "s1223"
    alpha_array = list(range(0, 11))
    analysis_parameters = {
        "reynolds": 700_000.0,
        "iterations": 1000,
    }
    chord = 1.0  # [m] Use the real chord value if you need x_cp in meters.
    console = Console()

    xfoil_service = XfoilService()
    df_reference: DataFrame[ChordwisePressureCoefficient] | None = None
    xcp_array: list[float] = []
    delta_cp_array = []
    xcp_m_array: list[float] = []

    console.print(
        Panel.fit(
            (
                f"[bold cyan]Centro de pressão[/bold cyan]\n"
                f"Airfoil: [green]{airfoil_name.upper()}[/green]  |  "
                f"Re: [yellow]{analysis_parameters['reynolds']:.0f}[/yellow]  |  "
                f"Iter: [yellow]{analysis_parameters['iterations']}[/yellow]"
            ),
            title="Análise XFOIL",
        )
    )

    results_table = Table(title="Resultados por ângulo de ataque")
    results_table.add_column("Alpha (deg)", justify="right", style="cyan")
    results_table.add_column("x_cp/c", justify="right", style="green")
    results_table.add_column("x_cp (m)", justify="right", style="magenta")

    for alpha in alpha_array:
        df_cp: DataFrame[ChordwisePressureCoefficient] = (
            xfoil_service.get_chordwise_pressure_coefficient(
                Airfoil(airfoil_name),
                alpha=float(alpha),
                **analysis_parameters,
            )
        )
        if df_reference is None:
            df_reference = df_cp
        x_cp_over_c, _cn, _cm_le = center_of_pressure(df_cp)
        x_cp_m = x_cp_over_c * chord
        xcp_array.append(x_cp_over_c)
        xcp_m_array.append(x_cp_m)
        delta_cp_array.append(chordwise_pressure_difference(df_cp))
        results_table.add_row(
            f"{alpha:.0f}",
            f"{x_cp_over_c:.6f}",
            f"{x_cp_m:.6f}",
        )

    if df_reference is None:
        raise RuntimeError("No pressure data generated.")

    console.print(results_table)

    cmap = plt.get_cmap("viridis", len(alpha_array))
    fig = plt.figure(figsize=(13, 8))
    grid = fig.add_gridspec(2, 2, height_ratios=[2, 3])
    ax_profile = fig.add_subplot(grid[0, :])
    ax_delta_cp = fig.add_subplot(grid[1, 0])
    ax_xcp = fig.add_subplot(grid[1, 1])
    fig.suptitle(f"Centro de pressão e distribuição de pressão - {airfoil_name.upper()}")

    x_profile = df_reference["x"].to_numpy()
    y_profile = df_reference["y"].to_numpy()
    ax_profile.plot(x_profile, y_profile, color="black", linewidth=1.2, label="Perfil")
    ax_profile.axhline(0, color="gray", linewidth=0.8, linestyle="--")
    for idx, alpha in enumerate(alpha_array):
        color = cmap(idx)
        x_cp_over_c = xcp_array[idx]
        ax_profile.scatter([x_cp_over_c], [0], color=color, s=26, zorder=3)
        ax_profile.text(
            x_cp_over_c,
            0.004,
            f"{alpha}°",
            fontsize=8,
            ha="center",
            va="bottom",
            color=color,
        )
    ax_profile.set_xlim(0, 1)
    ax_profile.set_ylabel("y/c")
    ax_profile.set_aspect("equal", adjustable="box")
    ax_profile.grid(True, alpha=0.3)
    ax_profile.set_title("Perfil e posição do centro de pressão para cada ângulo")

    for idx, alpha in enumerate(alpha_array):
        color = cmap(idx)
        x_common, delta_cp = delta_cp_array[idx]
        ax_delta_cp.plot(x_common, delta_cp, color=color, linewidth=1.2, label=f"{alpha}°")
    ax_delta_cp.axhline(0, color="gray", linewidth=0.8, linestyle="--")
    ax_delta_cp.set_xlabel("x/c")
    ax_delta_cp.set_ylabel("ΔCp = Cp_lower - Cp_upper")
    ax_delta_cp.grid(True, alpha=0.3)
    ax_delta_cp.set_title("Distribuição de pressão ao longo da corda")
    ax_delta_cp.legend(title="Alpha", fontsize=8, ncol=2)

    ax_xcp.plot(alpha_array, xcp_array, marker="o", linewidth=1.5, color="tab:red")
    ax_xcp.set_xlabel("alpha [°]")
    ax_xcp.set_ylabel("x_cp/c")
    ax_xcp.grid(True, alpha=0.3)
    ax_xcp.set_title("Evolução do centro de pressão com alpha")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
