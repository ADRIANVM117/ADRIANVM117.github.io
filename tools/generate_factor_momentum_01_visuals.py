"""Generate the approved Factor Momentum 01 visual resources.

This tool is intentionally read-only with respect to the scientific project.
It decodes the certified Plotly payload embedded in cell 67 of Foundations
for the QQQ decomposition, and reads the certified text outputs in cells 78
and 11 for the two summary comparisons.  It does not execute a notebook,
fit a regression, construct a signal, or read data from an external source.

Run from the Editorial & Warm root:

    python tools/generate_factor_momentum_01_visuals.py
"""

from __future__ import annotations

import base64
import argparse
import json
import re
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter, MultipleLocator


SITE_ROOT = Path(__file__).resolve().parents[1]
RESEARCH_ROOT = SITE_ROOT.parent / "quant-research-notes"
FACTOR_ROOT = RESEARCH_ROOT / "Momentum_systematic_strategies" / "02_factor_momentum"
FOUNDATIONS_NOTEBOOK = FACTOR_ROOT / "notebooks" / "01_factor_momentum_foundations.ipynb"
SIGNAL_NOTEBOOK = FACTOR_ROOT / "notebooks" / "02_factor_momentum_signal_test.ipynb"
AUDIT = FACTOR_ROOT / "AUDITORIA_FINAL_INTEGRADA.md"
OUTPUT_DIR = SITE_ROOT / "img" / "factor_momentum" / "01_foundations"

# Stable notebook locations audited for this publication.  The tool validates
# their output contracts rather than re-running their source code.
FOUNDATIONS_DECOMPOSITION_CELL = 67
FOUNDATIONS_R2_CELL = 78
SIGNAL_PERFORMANCE_CELL = 11

BACKGROUND = "#F7F5EF"
INK = "#252522"
WARM_GRAY = "#776F65"
LIGHT_GRAY = "#D9D3C9"
TERRACOTTA = "#A9684F"
SOFT_GREEN = "#5E7166"

EXPECTED_R2 = {
    "QQQ": {"MKT": 0.880, "MKT + SIZE + GV": 0.972},
    "XLE": {"MKT": 0.362, "MKT + SIZE + GV": 0.559},
    "XLF": {"MKT": 0.705, "MKT + SIZE + GV": 0.865},
}
EXPECTED_RETURNS = {
    "QQQ": {"Systematic Momentum": 12.918, "Buy & Hold": 19.008},
    "XLE": {"Systematic Momentum": 15.571, "Buy & Hold": 14.879},
    "XLF": {"Systematic Momentum": 7.995, "Buy & Hold": 12.118},
}


def load_notebook(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"Notebook source not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def output_data(notebook: dict, cell_index: int, mime: str) -> object:
    """Return one certified output payload without executing the cell."""
    try:
        cell = notebook["cells"][cell_index]
    except IndexError as error:
        raise IndexError(f"Expected cell {cell_index} is absent.") from error
    for output in cell.get("outputs", []):
        data = output.get("data", {})
        if mime in data:
            return data[mime]
    raise ValueError(f"Cell {cell_index} has no {mime} output payload.")


def output_text(notebook: dict, cell_index: int) -> str:
    value = output_data(notebook, cell_index, "text/plain")
    return "".join(value) if isinstance(value, list) else str(value)


def decode_plotly_float64(payload: dict) -> np.ndarray:
    """Decode Plotly's explicit little-endian f8 notebook representation."""
    if payload.get("dtype") != "f8" or not payload.get("bdata"):
        raise ValueError("The certified Plotly series is not the expected f8 payload.")
    values = np.frombuffer(base64.b64decode(payload["bdata"]), dtype="<f8")
    if not np.isfinite(values).all():
        raise ValueError("The certified Plotly series contains non-finite values.")
    return values


def load_qqq_decomposition(notebook: dict) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """Extract the three unmodified 126-session series from Foundations cell 67."""
    plot = output_data(notebook, FOUNDATIONS_DECOMPOSITION_CELL, "application/vnd.plotly.v1+json")
    traces = {trace.get("name"): trace for trace in plot.get("data", [])}
    expected_names = {"total", "systematic", "residual"}
    if set(traces) != expected_names:
        raise ValueError(f"Unexpected decomposition traces: {sorted(traces)}")
    dates = np.array([datetime.fromisoformat(value) for value in traces["total"]["x"]])
    if dates.size != 1854 or dates[0].date().isoformat() != "2019-07-05" or dates[-1].date().isoformat() != "2026-11-17":
        raise ValueError("The QQQ decomposition window differs from the certified Plotly output.")
    series = {name: decode_plotly_float64(traces[name]["y"]) for name in expected_names}
    if any(values.size != dates.size for values in series.values()):
        raise ValueError("The QQQ decomposition traces do not share the certified calendar.")
    if not np.allclose(series["total"], series["systematic"] + series["residual"], rtol=0.0, atol=1e-12):
        raise ValueError("The extracted components do not reconstruct total momentum.")
    return dates, series


def parse_r2_output(text: str) -> dict[str, dict[str, float]]:
    """Read the six values displayed in the certified cell 78 table."""
    # Notebook output was saved with a legacy-rendered Polars border, so the
    # parser intentionally keys off the data columns rather than a glyph.
    matches = re.findall(
        r"(?m)^.*?(QQQ|XLE|XLF).*?(market|full).*?1979.*?([0-9.]+)",
        text,
    )
    observed: dict[str, dict[str, float]] = {asset: {} for asset in EXPECTED_R2}
    for asset, model, value in matches:
        label = "MKT" if model == "market" else "MKT + SIZE + GV"
        observed[asset][label] = float(value)
    if observed != EXPECTED_R2:
        raise ValueError(f"Cell {FOUNDATIONS_R2_CELL} does not match the approved R² values: {observed}")
    return observed


def parse_performance_output(text: str) -> dict[str, dict[str, float]]:
    """Read Buy & Hold and Systematic Momentum from certified cell 11 output."""
    observed: dict[str, dict[str, float]] = {asset: {} for asset in EXPECTED_RETURNS}
    for asset in EXPECTED_RETURNS:
        buy_hold = re.search(rf"(?m)^.*?{asset}.*?Buy & Hold.*?([0-9.]+)", text)
        systematic = re.search(rf"(?m)^.*?{asset}.*?Systematic.*?([0-9.]+)", text)
        if not buy_hold or not systematic:
            raise ValueError(f"Certified performance table is incomplete for {asset}.")
        observed[asset]["Buy & Hold"] = float(buy_hold.group(1))
        observed[asset]["Systematic Momentum"] = float(systematic.group(1))
    if observed != EXPECTED_RETURNS:
        raise ValueError(f"Cell {SIGNAL_PERFORMANCE_CELL} does not match approved annualized returns: {observed}")
    return observed


def verify_audit() -> None:
    """Ensure the frozen integration audit carries every published summary value."""
    if not AUDIT.is_file():
        raise FileNotFoundError(f"Integrated audit not found: {AUDIT}")
    text = AUDIT.read_text(encoding="utf-8")
    required = ("0.880", "0.972", "0.362", "0.559", "0.705", "0.865", "12.918%", "19.008%", "15.571%", "14.879%", "7.995%", "12.118%")
    missing = [value for value in required if value not in text]
    if missing:
        raise ValueError(f"Integrated audit is missing expected certified values: {missing}")


def style_axis(axis: plt.Axes, *, grid: str = "y") -> None:
    axis.set_facecolor(BACKGROUND)
    axis.grid(axis=grid, color=LIGHT_GRAY, linewidth=0.7, zorder=0)
    axis.tick_params(axis="both", colors=WARM_GRAY, labelsize=8.5, length=0)
    for spine in axis.spines.values():
        spine.set_visible(False)


def save_figure(figure: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=180, facecolor=BACKGROUND)
    plt.close(figure)


def output_paths(language: str) -> tuple[Path, Path, Path]:
    """Return language-specific paths without overwriting approved assets."""
    directory = OUTPUT_DIR if language == "es" else OUTPUT_DIR / "en"
    return (
        directory / "momentum_decomposition_qqq.png",
        directory / "factor_attribution_r2_comparison.png",
        directory / "idealized_signal_performance.png",
    )


def build_momentum_decomposition(
    dates: np.ndarray,
    series: dict[str, np.ndarray],
    path: Path,
    language: str,
) -> None:
    figure, axis = plt.subplots(figsize=(11.8, 5.8))
    figure.patch.set_facecolor(BACKGROUND)
    lines = (
        (("total", "Momentum total", INK, 1.95), ("systematic", "Momentum sistemático", TERRACOTTA, 1.75), ("residual", "Momentum residual", WARM_GRAY, 1.45))
        if language == "es"
        else (("total", "Total Momentum", INK, 1.95), ("systematic", "Systematic Momentum", TERRACOTTA, 1.75), ("residual", "Residual Momentum", WARM_GRAY, 1.45))
    )
    # Cell 67 multiplies the log-return sums by 100 before serializing the
    # Plotly payload, so these certified y values are already percentages.
    for key, label, color, width in lines:
        axis.plot(dates, series[key], label=label, color=color, linewidth=width)
    axis.axhline(0, color=INK, linewidth=0.8, zorder=1)
    axis.set_xlim(dates[0], dates[-1])
    axis.xaxis.set_major_locator(mdates.YearLocator())
    axis.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    if language == "es":
        axis.set_ylabel("Retorno logarítmico acumulado (%)", color=INK, fontsize=8.7)
        axis.set_title("FACTOR MOMENTUM · DESCOMPOSICIÓN HISTÓRICA DE QQQ", loc="left", color=INK, fontsize=12, fontweight="bold", pad=18)
        axis.text(0, 1.015, "Momentum de 126 sesiones · componente sistemático = intercepto + MKT + SIZE + GV", transform=axis.transAxes, color=WARM_GRAY, fontsize=8.5)
        axis.text(0, -0.19, "Atribución histórica con factores realizados; no es un pronóstico previo a la sesión.", transform=axis.transAxes, color=WARM_GRAY, fontsize=8.0)
    else:
        axis.set_ylabel("Cumulative Log Return (%)", color=INK, fontsize=8.7)
        axis.set_xlabel("Trading Sessions", color=INK, fontsize=8.7)
        axis.set_title("FACTOR MOMENTUM · HISTORICAL DECOMPOSITION OF QQQ", loc="left", color=INK, fontsize=12, fontweight="bold", pad=18)
        axis.text(0, 1.015, "126-session momentum · systematic component = intercept + MKT + SIZE + GV", transform=axis.transAxes, color=WARM_GRAY, fontsize=8.5)
        axis.text(0, -0.19, "Historical attribution with realized factors; not an ex-ante return forecast.", transform=axis.transAxes, color=WARM_GRAY, fontsize=8.0)
    axis.legend(loc="upper left", ncol=3, frameon=False, fontsize=8.3, labelcolor=INK, handlelength=2.7)
    style_axis(axis)
    figure.subplots_adjust(left=0.105, right=0.98, top=0.85, bottom=0.19)
    save_figure(figure, path)


def build_r2_comparison(values: dict[str, dict[str, float]], path: Path, language: str) -> None:
    figure, axis = plt.subplots(figsize=(11.8, 5.5))
    figure.patch.set_facecolor(BACKGROUND)
    assets = list(values)
    positions = np.arange(len(assets))
    width = 0.29
    market = [values[asset]["MKT"] for asset in assets]
    full = [values[asset]["MKT + SIZE + GV"] for asset in assets]
    bars_market = axis.bar(positions - width / 2, market, width, color=WARM_GRAY, label="MKT", zorder=2)
    bars_full = axis.bar(positions + width / 2, full, width, color=TERRACOTTA, label="MKT + SIZE + GV", zorder=2)
    for bars in (bars_market, bars_full):
        for bar in bars:
            axis.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.018, f"{bar.get_height():.3f}", ha="center", va="bottom", color=INK, fontsize=8.5, fontweight="bold")
    axis.set_ylim(0, 1.08)
    axis.yaxis.set_major_locator(MultipleLocator(0.2))
    axis.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.1f}"))
    axis.set_xticks(positions, assets, color=INK, fontsize=10)
    axis.set_ylabel("R² fuera de muestra" if language == "es" else "Out-of-sample R²", color=INK, fontsize=8.7)
    # Keep the legend in a dedicated header band.  It must not compete with
    # the high QQQ full-model label while retaining the approved R² scale.
    if language == "es":
        figure.text(0.09, 0.955, "FACTOR MOMENTUM · ATRIBUCIÓN FACTORIAL", color=INK, fontsize=12, fontweight="bold")
        figure.text(0.09, 0.922, "Mismo calendario de atribución · coeficientes estimados hasta t−1", color=WARM_GRAY, fontsize=8.5)
        axis.text(0, -0.20, "Atribución contemporánea; no pronóstico previo a la sesión.", transform=axis.transAxes, color=WARM_GRAY, fontsize=8.0)
    else:
        figure.text(0.09, 0.955, "FACTOR MOMENTUM · FACTOR ATTRIBUTION", color=INK, fontsize=12, fontweight="bold")
        figure.text(0.09, 0.922, "Same attribution calendar · coefficients estimated through t−1", color=WARM_GRAY, fontsize=8.5)
        axis.text(0, -0.20, "Contemporaneous attribution; not an ex-ante forecast.", transform=axis.transAxes, color=WARM_GRAY, fontsize=8.0)
    figure.legend(
        handles=[bars_market, bars_full],
        labels=["MKT", "MKT + SIZE + GV"],
        loc="upper left",
        bbox_to_anchor=(0.09, 0.895),
        ncol=2,
        frameon=False,
        fontsize=8.4,
        labelcolor=INK,
        handlelength=2.5,
    )
    style_axis(axis)
    figure.subplots_adjust(left=0.09, right=0.98, top=0.75, bottom=0.20)
    save_figure(figure, path)


def build_idealized_performance(values: dict[str, dict[str, float]], path: Path, language: str) -> None:
    figure, axis = plt.subplots(figsize=(11.8, 5.5))
    figure.patch.set_facecolor(BACKGROUND)
    assets = list(values)
    positions = np.arange(len(assets))
    width = 0.29
    systematic = [values[asset]["Systematic Momentum"] for asset in assets]
    buy_hold = [values[asset]["Buy & Hold"] for asset in assets]
    bars_systematic = axis.bar(positions - width / 2, systematic, width, color=TERRACOTTA, label="Systematic Momentum", zorder=2)
    bars_buy_hold = axis.bar(positions + width / 2, buy_hold, width, color=SOFT_GREEN, label="Buy & Hold", zorder=2)
    for bars in (bars_systematic, bars_buy_hold):
        for bar in bars:
            axis.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.34, f"{bar.get_height():.3f}%", ha="center", va="bottom", color=INK, fontsize=8.5, fontweight="bold")
    axis.set_ylim(0, 22.5)
    axis.yaxis.set_major_locator(MultipleLocator(5))
    axis.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.0f}%"))
    axis.set_xticks(positions, assets, color=INK, fontsize=10)
    if language == "es":
        axis.set_ylabel("Retorno anualizado histórico", color=INK, fontsize=8.7)
        axis.set_title("FACTOR MOMENTUM · RESULTADOS ECONÓMICOS IDEALIZADOS", loc="left", color=INK, fontsize=12, fontweight="bold", pad=18)
        axis.text(0, 1.015, "Comparación histórica de señales de momentum a 126 sesiones", transform=axis.transAxes, color=WARM_GRAY, fontsize=8.5)
        axis.text(0, -0.20, "Long/cash idealizado · efectivo al 0% · antes de costos de implementación.", transform=axis.transAxes, color=WARM_GRAY, fontsize=8.0)
    else:
        axis.set_ylabel("Annualized Historical Return", color=INK, fontsize=8.7)
        axis.set_title("FACTOR MOMENTUM · IDEALIZED ECONOMIC RESULTS", loc="left", color=INK, fontsize=12, fontweight="bold", pad=18)
        axis.text(0, 1.015, "Historical comparison of 126-session momentum signals", transform=axis.transAxes, color=WARM_GRAY, fontsize=8.5)
        axis.text(0, -0.20, "Idealized long/cash · cash earns 0% · before implementation costs.", transform=axis.transAxes, color=WARM_GRAY, fontsize=8.0)
    axis.legend(loc="upper left", ncol=2, frameon=False, fontsize=8.4, labelcolor=INK, handlelength=2.5)
    style_axis(axis)
    figure.subplots_adjust(left=0.09, right=0.98, top=0.85, bottom=0.20)
    save_figure(figure, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate approved Factor Momentum 01 visuals.")
    parser.add_argument("--lang", choices=("es", "en"), default="es", help="Language of visible figure labels.")
    args = parser.parse_args()
    foundations = load_notebook(FOUNDATIONS_NOTEBOOK)
    signals = load_notebook(SIGNAL_NOTEBOOK)
    verify_audit()
    dates, series = load_qqq_decomposition(foundations)
    r2_values = parse_r2_output(output_text(foundations, FOUNDATIONS_R2_CELL))
    performance_values = parse_performance_output(output_text(signals, SIGNAL_PERFORMANCE_CELL))
    momentum_path, r2_path, performance_path = output_paths(args.lang)
    build_momentum_decomposition(dates, series, momentum_path, args.lang)
    build_r2_comparison(r2_values, r2_path, args.lang)
    build_idealized_performance(performance_values, performance_path, args.lang)
    print(f"LANG={args.lang}")
    print(f"FIGURE_1={momentum_path}")
    print(f"FIGURE_1_SOURCE={FOUNDATIONS_NOTEBOOK.name}: cell {FOUNDATIONS_DECOMPOSITION_CELL}; {dates[0].date()} to {dates[-1].date()}; n={dates.size}")
    print(f"FIGURE_2={r2_path}")
    print(f"FIGURE_2_SOURCE={FOUNDATIONS_NOTEBOOK.name}: cell {FOUNDATIONS_R2_CELL}; values={r2_values}")
    print(f"FIGURE_3={performance_path}")
    print(f"FIGURE_3_SOURCE={SIGNAL_NOTEBOOK.name}: cell {SIGNAL_PERFORMANCE_CELL}; values={performance_values}")


if __name__ == "__main__":
    main()
