"""Generate reproducible Volatility Targeting 03 economic visual resources.

The scientific inputs come directly from the certified policy histories and
benchmark construction cells in notebook 03.  The notebook is executed in
memory only; this script never writes to it or reconstructs returns from
adjusted prices.

Run from the Editorial & Warm root with the volatility_target virtualenv:

    ..\\quant-research-notes\\volatility_target\\.venv\\Scripts\\python.exe \
        tools\\generate_vt03_economic_visuals.py
"""

from __future__ import annotations

import argparse
import json
import math
import os
from io import BytesIO
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from matplotlib.ticker import MaxNLocator, MultipleLocator


SITE_ROOT = Path(__file__).resolve().parents[1]
RESEARCH_ROOT = SITE_ROOT.parent / "quant-research-notes"
NOTEBOOK = (
    RESEARCH_ROOT
    / "volatility_target"
    / "01_rebalancing_policies"
    / "03_economic_statistic_evaluation.ipynb"
)
OUTPUT_ROOT = SITE_ROOT / "img" / "volatility_targeting" / "03_economic"
LANGUAGE = "es"
OUTPUT_DIR = OUTPUT_ROOT
GIF_PATH = OUTPUT_DIR / "cumulative_rebalancing_costs.gif"
GIF_FRAME_PATH = OUTPUT_DIR / "cumulative_rebalancing_costs_final_frame.png"
WEALTH_PATH = OUTPUT_DIR / "normalized_wealth.png"
DRAWDOWN_PATH = OUTPUT_DIR / "historical_drawdowns.png"

# These are the exact cells that validate the source policy histories and build
# the two notebook-defined benchmarks.  They are executed in memory, in order.
CELL_IDS = (
    "load-validated-policy-histories",
    "build-benchmark-b1",
    "build-benchmark-b2",
    "build-comparability-panel",
)

INITIAL_NAV_USD = 10_891.246187363835
EXPECTED_FINAL_NAV = {
    "P0 — Daily": 20_946.398124753934,
    "P1 — Banda 5 pp": 22_024.794436598226,
    "P2 — Banda 10 pp": 21_982.64015029923,
    "B1 — Buy & Hold SPY": 30_797.605472,
    "B2 — Asignación estática 60/40": 22_834.661758,
}
EXPECTED_OPERATING_TOTALS = {
    "P0 — Daily": (1_547, 1_278.516548),
    "P1 — Banda 5 pp": (263, 263.0),
    "P2 — Banda 10 pp": (115, 115.0),
}
POLICIES = (
    "P0 — Daily",
    "P1 — Banda 5 pp",
    "P2 — Banda 10 pp",
    "B1 — Buy & Hold SPY",
    "B2 — Asignación estática 60/40",
)
OPERATING_POLICIES = POLICIES[:3]
DISPLAY_NAMES_ES = {
    "P0 — Daily": "P0 · Diario",
    "P1 — Banda 5 pp": "P1 · Banda ±5 pp",
    "P2 — Banda 10 pp": "P2 · Banda ±10 pp",
    "B1 — Buy & Hold SPY": "B1 · Buy & Hold SPY",
    "B2 — Asignación estática 60/40": "B2 · 60% SPY / 40% efectivo",
}
DISPLAY_NAMES_EN = {
    "P0 — Daily": "P0 · Daily",
    "P1 — Banda 5 pp": "P1 · ±5 pp Band",
    "P2 — Banda 10 pp": "P2 · ±10 pp Band",
    "B1 — Buy & Hold SPY": "B1 · Buy & Hold SPY",
    "B2 — Asignación estática 60/40": "B2 · 60% SPY / 40% cash",
}
TEXT_BY_LANGUAGE = {
    "es": {
        "activity_title": "VOLATILITY TARGETING · ACTIVIDAD OPERATIVA Y COSTOS",
        "costs_note": "Costos registrados = comisión + IVA · el slippage ya está incorporado en los precios de ejecución",
        "trades_title": "OPERACIONES EJECUTADAS ACUMULADAS",
        "costs_title": "COSTOS MONETARIOS REGISTRADOS ACUMULADOS",
        "trades_y": "Operaciones",
        "summary_unit": "ops",
        "wealth_title": "CRECIMIENTO DEL PATRIMONIO",
        "wealth_subtitle": "NAV de cierre normalizado al capital inicial común",
        "wealth_y": "Índice de riqueza",
        "drawdown_title": "DRAWDOWNS HISTÓRICOS",
        "drawdown_subtitle": "Caída desde el máximo histórico de cada trayectoria NAV",
    },
    "en": {
        "activity_title": "VOLATILITY TARGETING · TRADING ACTIVITY AND COSTS",
        "costs_note": "Recorded costs = commission + VAT · slippage is already included in execution prices",
        "trades_title": "CUMULATIVE EXECUTED TRADES",
        "costs_title": "CUMULATIVE RECORDED TRADING COSTS",
        "trades_y": "Trades",
        "summary_unit": "trades",
        "wealth_title": "WEALTH GROWTH",
        "wealth_subtitle": "Closing NAV normalized to common initial capital",
        "wealth_y": "Wealth Index",
        "drawdown_title": "HISTORICAL DRAWDOWNS",
        "drawdown_subtitle": "Decline from each portfolio's historical NAV peak",
    },
}
DISPLAY_NAMES = DISPLAY_NAMES_ES
TEXT = TEXT_BY_LANGUAGE[LANGUAGE]
COLORS = {
    "P0 — Daily": "#252522",
    "P1 — Banda 5 pp": "#A9684F",
    "P2 — Banda 10 pp": "#776F65",
    "B1 — Buy & Hold SPY": "#5E7166",
    "B2 — Asignación estática 60/40": "#927B60",
}
LINESTYLES = {
    "P0 — Daily": "-",
    "P1 — Banda 5 pp": "-",
    "P2 — Banda 10 pp": "-",
    "B1 — Buy & Hold SPY": (0, (5, 2)),
    "B2 — Asignación estática 60/40": (0, (2, 2)),
}

BACKGROUND = "#F7F5EF"
INK = "#252522"
WARM_GRAY = "#776F65"
GRID = "#D9D3C9"
TERRACOTTA = "#A9684F"


def configure_language(language: str) -> None:
    """Select editorial labels and output paths without altering ES assets."""
    if language not in TEXT_BY_LANGUAGE:
        raise ValueError(f"Unsupported language: {language}")
    global LANGUAGE, DISPLAY_NAMES, TEXT, OUTPUT_DIR, GIF_PATH, GIF_FRAME_PATH, WEALTH_PATH, DRAWDOWN_PATH
    LANGUAGE = language
    DISPLAY_NAMES = DISPLAY_NAMES_EN if language == "en" else DISPLAY_NAMES_ES
    TEXT = TEXT_BY_LANGUAGE[language]
    OUTPUT_DIR = OUTPUT_ROOT / "en" if language == "en" else OUTPUT_ROOT
    GIF_PATH = OUTPUT_DIR / "cumulative_rebalancing_costs.gif"
    GIF_FRAME_PATH = OUTPUT_DIR / "cumulative_rebalancing_costs_final_frame.png"
    WEALTH_PATH = OUTPUT_DIR / "normalized_wealth.png"
    DRAWDOWN_PATH = OUTPUT_DIR / "historical_drawdowns.png"


def format_display_date(value) -> str:
    """Use the approved editorial date format for the selected image locale."""
    return value.strftime("%b %d, %Y") if LANGUAGE == "en" else value.strftime("%d %b %Y")


def notebook_cell(cell_id: str) -> str:
    """Return a notebook cell verbatim, without changing the notebook."""
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    for cell in notebook["cells"]:
        if cell.get("id") == cell_id:
            return "".join(cell["source"])
    raise KeyError(f"Notebook cell not found: {cell_id}")


def execute_certified_histories() -> dict[str, object]:
    """Build the five validated histories under notebook 03 conventions."""
    namespace: dict[str, object] = {"__name__": "__vt03_visual_generator__"}
    original_cwd = Path.cwd()
    try:
        # This lets the notebook prefer the local certified Parquets and SPY
        # source instead of changing its reproducibility logic.
        os.chdir(RESEARCH_ROOT / "volatility_target")
        for cell_id in CELL_IDS:
            source = notebook_cell(cell_id)
            exec(compile(source, f"{NOTEBOOK.name}:{cell_id}", "exec"), namespace)
    finally:
        os.chdir(original_cwd)

    histories = {
        "P0 — Daily": namespace["policy_p0"],
        "P1 — Banda 5 pp": namespace["policy_p1"],
        "P2 — Banda 10 pp": namespace["policy_p2"],
        "B1 — Buy & Hold SPY": namespace["benchmark_b1"],
        "B2 — Asignación estática 60/40": namespace["benchmark_b2"],
    }
    manifest = namespace["manifest"]
    if float(manifest["initial_capital"]["net_usd"]) != INITIAL_NAV_USD:
        raise ValueError("The notebook initial NAV differs from the certified convention.")

    reference_dates = histories[POLICIES[0]]["session_date"].to_list()
    if not reference_dates:
        raise ValueError("The certified histories are empty.")
    for policy, history in histories.items():
        if history["session_date"].to_list() != reference_dates:
            raise ValueError(f"{policy} does not share the notebook calendar.")
        if float(history["portfolio_value_close"][-1]) <= 0:
            raise ValueError(f"{policy} has an invalid final NAV.")
        if not math.isclose(
            float(history["portfolio_value_close"][-1]),
            EXPECTED_FINAL_NAV[policy],
            rel_tol=0.0,
            abs_tol=1e-6,
        ):
            raise ValueError(f"{policy} final NAV differs from the certified notebook result.")
    return histories


def cumulative_operating_series(histories: dict[str, object]) -> dict[str, dict[str, np.ndarray]]:
    """Return real, daily cumulative execution and registered-cost series."""
    cumulative: dict[str, dict[str, np.ndarray]] = {}
    for policy in OPERATING_POLICIES:
        history = histories[policy]
        dates = np.asarray(history["session_date"].to_list(), dtype=object)
        executed = np.asarray(history["trade_executed"].to_list(), dtype=np.int64)
        registered_cost = np.asarray(history["total_cost"].to_list(), dtype=float)
        if not np.isin(executed, (0, 1)).all():
            raise ValueError(f"{policy} has a non-boolean trade execution series.")
        if not np.isfinite(registered_cost).all() or (registered_cost < 0).any():
            raise ValueError(f"{policy} has an invalid registered-cost series.")
        expected_executions, expected_cost = EXPECTED_OPERATING_TOTALS[policy]
        if int(executed.sum()) != expected_executions or not math.isclose(
            float(registered_cost.sum()), expected_cost, rel_tol=0.0, abs_tol=1e-8
        ):
            raise ValueError(f"{policy} operating totals differ from the certified notebook result.")
        cumulative[policy] = {
            "dates": dates,
            "executions": np.cumsum(executed),
            "registered_cost": np.cumsum(registered_cost),
        }
    return cumulative


def setup_axis(axis: plt.Axes) -> None:
    axis.set_facecolor(BACKGROUND)
    axis.grid(axis="y", color=GRID, linewidth=0.65)
    axis.tick_params(axis="both", colors=WARM_GRAY, labelsize=8, length=0)
    for spine in axis.spines.values():
        spine.set_visible(False)


def draw_cost_frame(
    cumulative: dict[str, dict[str, np.ndarray]], endpoint: int, *, final: bool
) -> Image.Image:
    """Draw one un-interpolated cumulative execution/cost animation frame."""
    dates = cumulative[OPERATING_POLICIES[0]]["dates"]
    current_date = dates[endpoint]
    figure, axes = plt.subplots(
        2,
        1,
        figsize=(11.8, 7.0),
        sharex=True,
        gridspec_kw={"top": 0.83, "bottom": 0.13, "left": 0.10, "right": 0.96, "hspace": 0.30},
    )
    figure.patch.set_facecolor(BACKGROUND)
    visible = slice(0, endpoint + 1)

    for policy in OPERATING_POLICIES:
        series = cumulative[policy]
        common = {
            "color": COLORS[policy],
            "linewidth": 1.65,
            "drawstyle": "steps-post",
            "label": DISPLAY_NAMES[policy],
        }
        axes[0].plot(dates[visible], series["executions"][visible], **common)
        axes[1].plot(dates[visible], series["registered_cost"][visible], **common)

    for axis in axes:
        axis.axvline(current_date, color=TERRACOTTA, alpha=0.62, linewidth=0.95, zorder=1)
        axis.set_xlim(dates[0], dates[-1])
        setup_axis(axis)

    axes[0].set_title(TEXT["trades_title"], loc="left", color=INK, fontsize=9.2, fontweight="bold", pad=10)
    axes[0].set_ylabel(TEXT["trades_y"], color=INK, fontsize=8.4)
    axes[1].set_title(TEXT["costs_title"], loc="left", color=INK, fontsize=9.2, fontweight="bold", pad=10)
    axes[1].set_ylabel("USD", color=INK, fontsize=8.4)
    # Fixed scales let every frame communicate actual cumulative differences,
    # rather than a changing visual scale as the animation progresses.
    axes[0].set_ylim(0, 1_600)
    axes[0].yaxis.set_major_locator(MaxNLocator(nbins=8, integer=True))
    axes[1].set_ylim(0, 1_400)
    axes[1].yaxis.set_major_locator(MultipleLocator(200))
    axes[1].xaxis.set_major_locator(mdates.YearLocator())
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    axes[1].yaxis.set_major_formatter(lambda value, _: f"${value:,.0f}")
    axes[0].legend(loc="upper left", ncol=3, frameon=False, fontsize=8, labelcolor=INK, handlelength=2.4)

    figure.text(0.10, 0.955, TEXT["activity_title"], color=INK, fontsize=12, fontweight="bold")
    figure.text(
        0.10,
        0.922,
        TEXT["costs_note"],
        color=WARM_GRAY,
        fontsize=8.4,
    )
    figure.text(
        0.96,
        0.955,
        format_display_date(current_date),
        ha="right",
        color=INK if final else TERRACOTTA,
        fontsize=8.5,
        fontfamily="DejaVu Sans Mono",
    )

    if final:
        total_text = "   ".join(
            f"{DISPLAY_NAMES[policy].split(' · ')[0]}: {series['executions'][-1]:,} {TEXT['summary_unit']} · ${series['registered_cost'][-1]:,.2f}"
            for policy, series in ((p, cumulative[p]) for p in OPERATING_POLICIES)
        )
        figure.text(0.10, 0.058, total_text, color=INK, fontsize=8.1, fontfamily="DejaVu Sans Mono")

    buffer = BytesIO()
    figure.savefig(buffer, format="png", dpi=110, facecolor=BACKGROUND)
    plt.close(figure)
    buffer.seek(0)
    return Image.open(buffer).convert("P", palette=Image.Palette.ADAPTIVE, colors=128)


def build_cumulative_cost_gif(histories: dict[str, object]) -> tuple[dict[str, dict[str, np.ndarray]], int]:
    """Make an 11–12 second GIF from actual session observations only."""
    cumulative = cumulative_operating_series(histories)
    number_of_sessions = len(cumulative[OPERATING_POLICIES[0]]["dates"])
    # 111 actual session endpoints at 100 ms plus a 1,000 ms final state = 12 s.
    endpoints = np.unique(np.linspace(0, number_of_sessions - 1, 111, dtype=int))
    if endpoints[-1] != number_of_sessions - 1:
        raise ValueError("The animation does not end on the final trading session.")
    frames = [draw_cost_frame(cumulative, int(endpoint), final=False) for endpoint in endpoints]
    final_frame = draw_cost_frame(cumulative, number_of_sessions - 1, final=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    final_frame.save(GIF_FRAME_PATH, format="PNG")
    frames[-1] = final_frame
    frames[0].save(
        GIF_PATH,
        format="GIF",
        append_images=frames[1:],
        save_all=True,
        duration=[100] * (len(frames) - 1) + [1000],
        loop=0,
        optimize=True,
        disposal=2,
    )
    return cumulative, len(frames)


def build_normalized_wealth(histories: dict[str, object]) -> None:
    """Draw wealth only from each portfolio's certified NAV history."""
    figure, axis = plt.subplots(figsize=(11.8, 5.8))
    figure.patch.set_facecolor(BACKGROUND)
    reference_dates = histories[POLICIES[0]]["session_date"].to_list()
    for policy in POLICIES:
        history = histories[policy]
        nav = np.asarray(history["portfolio_value_close"].to_list(), dtype=float)
        if not np.isfinite(nav).all() or (nav <= 0).any():
            raise ValueError(f"{policy} has an invalid NAV series.")
        axis.plot(
            history["session_date"].to_list(),
            nav / INITIAL_NAV_USD,
            color=COLORS[policy],
            linestyle=LINESTYLES[policy],
            linewidth=1.7,
            label=DISPLAY_NAMES[policy],
        )
    axis.set_title(TEXT["wealth_title"], loc="left", color=INK, fontsize=12, fontweight="bold", pad=18)
    axis.text(0, 1.015, TEXT["wealth_subtitle"], transform=axis.transAxes, color=WARM_GRAY, fontsize=8.6)
    axis.set_ylabel(TEXT["wealth_y"], color=INK, fontsize=8.6)
    axis.set_xlim(reference_dates[0], reference_dates[-1])
    axis.xaxis.set_major_locator(mdates.YearLocator())
    axis.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    axis.legend(loc="upper left", ncol=3, frameon=False, fontsize=8, labelcolor=INK, handlelength=2.8)
    setup_axis(axis)
    figure.subplots_adjust(left=0.09, right=0.98, top=0.86, bottom=0.13)
    figure.savefig(WEALTH_PATH, dpi=180, facecolor=BACKGROUND)
    plt.close(figure)


def build_historical_drawdowns(histories: dict[str, object]) -> None:
    """Draw drawdowns from each portfolio's NAV and its own running maximum."""
    figure, axis = plt.subplots(figsize=(11.8, 5.8))
    figure.patch.set_facecolor(BACKGROUND)
    reference_dates = histories[POLICIES[0]]["session_date"].to_list()
    for policy in POLICIES:
        history = histories[policy]
        nav = np.asarray(history["portfolio_value_close"].to_list(), dtype=float)
        high_water_mark = np.maximum.accumulate(np.concatenate(([INITIAL_NAV_USD], nav)))[1:]
        drawdown = nav / high_water_mark - 1.0
        if (drawdown > 1e-10).any():
            raise ValueError(f"{policy} produces a positive drawdown.")
        axis.plot(
            history["session_date"].to_list(),
            drawdown,
            color=COLORS[policy],
            linestyle=LINESTYLES[policy],
            linewidth=1.7,
            label=DISPLAY_NAMES[policy],
        )
    axis.axhline(0, color=INK, linewidth=0.85)
    axis.set_title(TEXT["drawdown_title"], loc="left", color=INK, fontsize=12, fontweight="bold", pad=18)
    axis.text(0, 1.015, TEXT["drawdown_subtitle"], transform=axis.transAxes, color=WARM_GRAY, fontsize=8.6)
    axis.set_ylabel("Drawdown", color=INK, fontsize=8.6)
    axis.yaxis.set_major_formatter(lambda value, _: f"{value:.0%}")
    axis.set_xlim(reference_dates[0], reference_dates[-1])
    axis.xaxis.set_major_locator(mdates.YearLocator())
    axis.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    axis.legend(loc="lower left", ncol=3, frameon=False, fontsize=8, labelcolor=INK, handlelength=2.8)
    setup_axis(axis)
    figure.subplots_adjust(left=0.09, right=0.98, top=0.86, bottom=0.13)
    figure.savefig(DRAWDOWN_PATH, dpi=180, facecolor=BACKGROUND)
    plt.close(figure)


def main(language: str) -> None:
    configure_language(language)
    histories = execute_certified_histories()
    cumulative, gif_frames = build_cumulative_cost_gif(histories)
    build_normalized_wealth(histories)
    build_historical_drawdowns(histories)

    print(f"PERIOD={cumulative[OPERATING_POLICIES[0]]['dates'][0]} to {cumulative[OPERATING_POLICIES[0]]['dates'][-1]}")
    print(f"GIF_FRAMES={gif_frames} DURATION_SECONDS=12.0")
    for policy in OPERATING_POLICIES:
        series = cumulative[policy]
        print(
            f"{policy}: EXECUTED={series['executions'][-1]} "
            f"REGISTERED_COST_USD={series['registered_cost'][-1]:.8f}"
        )
    for policy in POLICIES:
        final_nav = float(histories[policy]["portfolio_value_close"][-1])
        print(f"{policy}: FINAL_NAV_USD={final_nav:.8f} WEALTH={final_nav / INITIAL_NAV_USD:.10f}")
    print(f"GIF={GIF_PATH}")
    print(f"GIF_FRAME={GIF_FRAME_PATH}")
    print(f"WEALTH={WEALTH_PATH}")
    print(f"DRAWDOWNS={DRAWDOWN_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--lang",
        choices=("es", "en"),
        default="es",
        help="Editorial language for visible chart text (default: es).",
    )
    main(parser.parse_args().lang)
