"""Generate reproducible visual resources for Volatility Targeting 04.

The calculations deliberately mirror Block 07 of
``03_economic_statistic_evaluation.ipynb``.  Source policy histories are read
only from the certified Parquet inputs; this tool never changes the notebook
or reconstructs the strategies from market prices.

Run from the Editorial & Warm root with the volatility-target environment:

    ..\\quant-research-notes\\volatility_target\\.venv\\Scripts\\python.exe \\
        tools\\generate_vt04_uncertainty_visuals.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from matplotlib.patches import FancyArrowPatch, Rectangle
from matplotlib.ticker import MultipleLocator


SITE_ROOT = Path(__file__).resolve().parents[1]
RESEARCH_ROOT = SITE_ROOT.parent / "quant-research-notes"
NOTEBOOK = (
    RESEARCH_ROOT
    / "volatility_target"
    / "01_rebalancing_policies"
    / "03_economic_statistic_evaluation.ipynb"
)
ARTIFACT_DIR = RESEARCH_ROOT / "volatility_target" / "artifacts" / "evaluation_inputs"
OUTPUT_DIR = SITE_ROOT / "img" / "volatility_targeting" / "04_uncertainty"

TRADEOFF_PATH = OUTPUT_DIR / "growth_vs_tracking_tradeoff.png"
BOOTSTRAP_SCHEME_PATH = OUTPUT_DIR / "circular_block_bootstrap_scheme.png"
INTERVALS_PATH = OUTPUT_DIR / "bootstrap_intervals_growth_and_mae.png"

POLICIES = {
    "P0": "policy_p0.parquet",
    "P1": "policy_p1.parquet",
    "P2": "policy_p2.parquet",
}

# Notebook Block 07 parameters.  Do not silently substitute other values.
INITIAL_NAV_USD = 10_891.246187363835
TARGET_VOLATILITY = 0.12
ROLLING_VOL_WINDOW = 21
TRADING_DAYS_PER_YEAR = 252
BOOTSTRAP_REPLICATIONS = 2_000
BOOTSTRAP_SEED = 42
BLOCK_LENGTHS = (21, 63)

# Editorial & Warm chart system, aligned with the VT02/VT03 visual resources.
BACKGROUND = "#F7F5EF"
INK = "#252522"
WARM_GRAY = "#776F65"
GRID = "#D9D3C9"
TERRACOTTA = "#A9684F"
P0_COLOR = "#252522"
P1_COLOR = "#A9684F"
P2_COLOR = "#776F65"
BLOCK_COLORS = {21: TERRACOTTA, 63: "#776F65"}

TEXT_BY_LANGUAGE = {
    "es": {
        "tradeoff_title": "VOLATILITY TARGETING \u00b7 CRECIMIENTO Y SEGUIMIENTO DEL OBJETIVO",
        "tradeoff_subtitle": "Diferencias observadas frente a P0 \u00b7 P1 y P2 usan la misma se\u00f1al EWMA",
        "policy_labels": ["P1 \u00b7 Banda \u00b15 pp", "P2 \u00b7 Banda \u00b110 pp"],
        "growth_heading": "DIFERENCIAL DE CRECIMIENTO LOGAR\u00cdTMICO ANUALIZADO",
        "growth_unit": "pp por a\u00f1o",
        "growth_note": "Un valor positivo favorece a la banda.",
        "mae_heading": "DIFERENCIAL DE MAE DE SEGUIMIENTO",
        "mae_unit": "pp",
        "mae_note": "Un valor positivo implica mayor error medio.",
        "scheme_title": "BOOTSTRAP CIRCULAR POR BLOQUES \u00b7 ESQUEMA DE REMUESTREO",
        "scheme_subtitle": "Diferenciales diarios emparejados por fecha \u00b7 2,000 remuestreos \u00b7 semilla 42",
        "paired_heading": "1. DIFERENCIAL EMPAREJADO",
        "paired_equation": r"$d_t = \log(1 + r_{t,\mathrm{banda}}) - \log(1 + r_{t,\mathrm{P0}})$",
        "dates": "FECHAS",
        "circular_note": "La serie es circular: el bloque puede continuar del final al inicio.",
        "selection_heading": "2. SELECCI\u00d3N DE BLOQUES CONSECUTIVOS",
        "selection_note": "No se remuestrean d\u00edas aislados: se conservan segmentos contiguos del diferencial.",
        "block_21": "BLOQUE 21",
        "complete_note": "... hasta completar n observaciones",
        "block_63": "BLOQUE 63",
        "long_block_note": "bloque m\u00e1s largo: preserva m\u00e1s dependencia temporal",
        "stat_heading": "3. ESTAD\u00cdSTICA",
        "stat_note": "media del diferencial remuestreado -> intervalo bootstrap al 95%",
        "intervals_title": "INCERTIDUMBRE ESTAD\u00cdSTICA \u00b7 INTERVALOS BOOTSTRAP AL 95%",
        "intervals_subtitle": "Diferenciales frente a P0 \u00b7 bootstrap circular por bloques emparejado por fecha",
        "interval_growth_heading": "CRECIMIENTO LOGAR\u00cdTMICO ANUALIZADO",
        "interval_mae_heading": "MAE DE SEGUIMIENTO DEL OBJETIVO 12%",
        "interval_growth_note": "Positivo favorece a la banda.",
        "interval_mae_note": "Positivo implica peor seguimiento.",
        "block_21_legend": "Bloque 21 sesiones",
        "block_63_legend": "Bloque 63 sesiones",
    },
    "en": {
        "tradeoff_title": "VOLATILITY TARGETING \u00b7 GROWTH AND VOLATILITY TARGET TRACKING",
        "tradeoff_subtitle": "Observed differences versus P0 \u00b7 P1 and P2 use the same EWMA signal",
        "policy_labels": ["P1 \u00b7 \u00b15 pp Band", "P2 \u00b7 \u00b110 pp Band"],
        "growth_heading": "ANNUALIZED LOG-GROWTH DIFFERENCE",
        "growth_unit": "pp per year",
        "growth_note": "A positive value favors the band.",
        "mae_heading": "TRACKING MAE DIFFERENCE",
        "mae_unit": "pp",
        "mae_note": "A positive value indicates higher average tracking error.",
        "scheme_title": "CIRCULAR BLOCK BOOTSTRAP \u00b7 RESAMPLING SCHEME",
        "scheme_subtitle": "Date-paired daily differentials \u00b7 2,000 resamples \u00b7 seed 42",
        "paired_heading": "1. PAIRED DIFFERENTIAL",
        "paired_equation": r"$d_t = \log(1 + r_{t,\mathrm{band}}) - \log(1 + r_{t,\mathrm{P0}})$",
        "dates": "DATES",
        "circular_note": "The series is circular: a block can continue from the end to the beginning.",
        "selection_heading": "2. CONSECUTIVE BLOCK SELECTION",
        "selection_note": "Individual days are not resampled: consecutive segments of the differential are retained.",
        "block_21": "21-SESSION BLOCK",
        "complete_note": "... until n observations are completed",
        "block_63": "63-SESSION BLOCK",
        "long_block_note": "longer block: preserves more temporal dependence",
        "stat_heading": "3. STATISTIC",
        "stat_note": "mean of the resampled differential -> 95% bootstrap interval",
        "intervals_title": "STATISTICAL UNCERTAINTY \u00b7 95% BOOTSTRAP INTERVALS",
        "intervals_subtitle": "Differences versus P0 \u00b7 date-paired circular block bootstrap",
        "interval_growth_heading": "ANNUALIZED LOG GROWTH",
        "interval_mae_heading": "TRACKING MAE FOR THE 12% TARGET",
        "interval_growth_note": "Positive values favor the band.",
        "interval_mae_note": "Positive values indicate worse tracking.",
        "block_21_legend": "21-Session Blocks",
        "block_63_legend": "63-Session Blocks",
    },
}
LANGUAGE = "es"
TEXT = TEXT_BY_LANGUAGE[LANGUAGE]


def configure_language(language: str) -> None:
    """Set localized labels and a language-specific output directory."""
    if language not in TEXT_BY_LANGUAGE:
        raise ValueError(f"Unsupported language: {language}")
    global LANGUAGE, TEXT, OUTPUT_DIR, TRADEOFF_PATH, BOOTSTRAP_SCHEME_PATH, INTERVALS_PATH
    LANGUAGE = language
    TEXT = TEXT_BY_LANGUAGE[language]
    OUTPUT_DIR = SITE_ROOT / "img" / "volatility_targeting" / "04_uncertainty"
    if language == "en":
        OUTPUT_DIR = OUTPUT_DIR / "en"
    TRADEOFF_PATH = OUTPUT_DIR / "growth_vs_tracking_tradeoff.png"
    BOOTSTRAP_SCHEME_PATH = OUTPUT_DIR / "circular_block_bootstrap_scheme.png"
    INTERVALS_PATH = OUTPUT_DIR / "bootstrap_intervals_growth_and_mae.png"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1_048_576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_certified_histories() -> dict[str, pl.DataFrame]:
    """Load only the notebook-certified P0/P1/P2 histories and verify hashes."""
    if not NOTEBOOK.is_file():
        raise FileNotFoundError(f"Notebook source not found: {NOTEBOOK}")
    manifest_path = ARTIFACT_DIR / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Certified manifest not found: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("artifact_type") != "volatility_target_policy_histories":
        raise ValueError("The artifact manifest does not contain volatility-target histories.")
    if not math.isclose(float(manifest["initial_capital"]["net_usd"]), INITIAL_NAV_USD):
        raise ValueError("Initial NAV differs from the approved notebook convention.")

    histories: dict[str, pl.DataFrame] = {}
    reference_dates: list[object] | None = None
    for short_name, filename in POLICIES.items():
        # The certified manifest remains the sole source of the human-facing
        # policy labels.  This prevents platform text-encoding differences
        # from affecting the reproducible data lookup.
        policy_name = next(
            (name for name in manifest["policies"] if name.startswith(f"{short_name} ")),
            None,
        )
        certificate = manifest["policies"].get(policy_name)
        path = ARTIFACT_DIR / filename
        if not certificate or not path.is_file():
            raise FileNotFoundError(f"Missing certified input for {short_name}.")
        if sha256_file(path) != certificate["sha256"]:
            raise ValueError(f"SHA-256 mismatch for {path.name}.")
        history = pl.read_parquet(path).sort("session_date")
        required = {"session_date", "portfolio_value_close"}
        if required.difference(history.columns) or history.height != 2_206:
            raise ValueError(f"{short_name} does not meet the certified history contract.")
        if history["policy"].n_unique() != 1 or history["policy"][0] != policy_name:
            raise ValueError(f"{short_name} has an inconsistent policy identifier.")
        dates = history["session_date"].to_list()
        if reference_dates is None:
            reference_dates = dates
        elif dates != reference_dates:
            raise ValueError("P0, P1, and P2 do not share the notebook calendar.")
        histories[short_name] = history
    return histories


def simple_and_log_returns(history: pl.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    nav = history["portfolio_value_close"].to_numpy().astype(float)
    if not np.isfinite(nav).all() or (nav <= 0).any():
        raise ValueError("A certified NAV history contains an invalid value.")
    previous_nav = np.concatenate(([INITIAL_NAV_USD], nav[:-1]))
    simple = nav / previous_nav - 1.0
    if (simple <= -1.0).any():
        raise ValueError("A policy return is less than or equal to -100%.")
    return simple, np.log1p(simple)


def rolling_abs_volatility_error(simple_returns: np.ndarray) -> np.ndarray:
    """Match the notebook's 21-session sample-std target tracking error."""
    if simple_returns.size < ROLLING_VOL_WINDOW:
        raise ValueError("Not enough observations for the rolling volatility window.")
    realized = np.array(
        [
            np.std(simple_returns[start : start + ROLLING_VOL_WINDOW], ddof=1)
            * math.sqrt(TRADING_DAYS_PER_YEAR)
            for start in range(simple_returns.size - ROLLING_VOL_WINDOW + 1)
        ]
    )
    errors = np.abs(realized - TARGET_VOLATILITY)
    if not np.isfinite(errors).all() or (errors < 0).any():
        raise ValueError("Invalid rolling target-tracking errors.")
    return errors


def paired_circular_block_bootstrap(
    values: np.ndarray, block_length: int, scale: float, seed: int = BOOTSTRAP_SEED
) -> np.ndarray:
    """Notebook cell 26: bootstrap one paired differential in circular blocks."""
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or values.size == 0 or not np.isfinite(values).all():
        raise ValueError("Bootstrap input must be a finite, non-empty vector.")
    rng = np.random.default_rng(seed)
    n_obs = values.size
    draws = np.empty(BOOTSTRAP_REPLICATIONS, dtype=float)
    offsets = np.arange(block_length)
    for replicate in range(BOOTSTRAP_REPLICATIONS):
        sampled_indices = np.empty(n_obs, dtype=int)
        position = 0
        while position < n_obs:
            start = int(rng.integers(0, n_obs))
            take = min(block_length, n_obs - position)
            sampled_indices[position : position + take] = (start + offsets[:take]) % n_obs
            position += take
        draws[replicate] = values[sampled_indices].mean() * scale
    return draws


def interval(values: np.ndarray, block_length: int, scale: float) -> dict[str, float]:
    draws = paired_circular_block_bootstrap(values, block_length, scale)
    return {
        "point": float(values.mean() * scale),
        "lower": float(np.quantile(draws, 0.025)),
        "upper": float(np.quantile(draws, 0.975)),
    }


def calculate_metrics(histories: dict[str, pl.DataFrame]) -> dict[str, dict[str, object]]:
    """Recreate exactly the paired growth and target-MAE comparisons in Block 07."""
    returns: dict[str, np.ndarray] = {}
    log_returns: dict[str, np.ndarray] = {}
    errors: dict[str, np.ndarray] = {}
    for short_name, history in histories.items():
        returns[short_name], log_returns[short_name] = simple_and_log_returns(history)
        errors[short_name] = rolling_abs_volatility_error(returns[short_name])

    results: dict[str, dict[str, object]] = {}
    for policy in ("P1", "P2"):
        growth = log_returns[policy] - log_returns["P0"]
        mae = errors[policy] - errors["P0"]
        if growth.size != 2_206 or mae.size != 2_186:
            raise ValueError(f"{policy}: paired differential length differs from notebook Block 07.")
        results[policy] = {
            "growth": {block: interval(growth, block, TRADING_DAYS_PER_YEAR * 100) for block in BLOCK_LENGTHS},
            "mae": {block: interval(mae, block, 100) for block in BLOCK_LENGTHS},
        }
    return results


def style_axis(axis: plt.Axes) -> None:
    axis.set_facecolor(BACKGROUND)
    axis.grid(axis="x", color=GRID, linewidth=0.7, zorder=0)
    axis.tick_params(axis="both", colors=WARM_GRAY, labelsize=8, length=0)
    for spine in axis.spines.values():
        spine.set_visible(False)


def add_title(figure: plt.Figure, title: str, subtitle: str) -> None:
    figure.text(0.09, 0.955, title, color=INK, fontsize=12, fontweight="bold")
    figure.text(0.09, 0.922, subtitle, color=WARM_GRAY, fontsize=8.5)


def create_tradeoff_figure(metrics: dict[str, dict[str, object]]) -> None:
    """Show the observed benefit / target-tracking trade-off without inference claims."""
    figure, axes = plt.subplots(1, 2, figsize=(11.8, 5.2), gridspec_kw={"wspace": 0.36})
    figure.patch.set_facecolor(BACKGROUND)
    add_title(
        figure,
        TEXT["tradeoff_title"],
        TEXT["tradeoff_subtitle"],
    )
    labels = TEXT["policy_labels"]
    positions = np.array([1, 0])
    growth = [metrics[policy]["growth"][21]["point"] for policy in ("P1", "P2")]
    mae = [metrics[policy]["mae"][21]["point"] for policy in ("P1", "P2")]

    panels = (
        (axes[0], growth, TEXT["growth_heading"], TEXT["growth_unit"], TEXT["growth_note"]),
        (axes[1], mae, TEXT["mae_heading"], TEXT["mae_unit"], TEXT["mae_note"]),
    )
    for axis, values, heading, unit, note in panels:
        colors = [P1_COLOR, P2_COLOR]
        axis.barh(positions, values, height=0.34, color=colors, zorder=2)
        axis.axvline(0, color=INK, linewidth=0.9, zorder=1)
        for y, value in zip(positions, values):
            axis.text(value + max(values) * 0.035, y, f"+{value:.3f} pp", va="center", color=INK, fontsize=9, fontweight="bold")
        axis.set_yticks(positions, labels)
        axis.set_title(heading, loc="left", color=INK, fontsize=9.1, fontweight="bold", pad=12)
        axis.set_xlabel(unit, color=INK, fontsize=8.5, labelpad=9)
        axis.text(0, -0.28, note, transform=axis.transAxes, color=WARM_GRAY, fontsize=8)
        axis.set_xlim(0, max(values) * 1.42)
        axis.xaxis.set_major_locator(MultipleLocator(0.2 if axis is axes[0] else 0.1))
        style_axis(axis)
    figure.subplots_adjust(left=0.17, right=0.97, top=0.79, bottom=0.22)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    figure.savefig(TRADEOFF_PATH, dpi=180, facecolor=BACKGROUND)
    plt.close(figure)


def add_sequence(axis: plt.Axes, y: float, length: int, label: str, color: str, start_x: float = 1.5) -> None:
    """Draw a sequence of consecutive observations without assigning fake data values."""
    width = 0.62
    for index in range(length):
        x = start_x + index * (width + 0.06)
        axis.add_patch(Rectangle((x, y), width, 0.52, facecolor=color, edgecolor=BACKGROUND, linewidth=1.0))
    axis.text(0.08, y + 0.26, label, va="center", color=INK, fontsize=8.5, fontweight="bold")


def create_bootstrap_scheme_figure() -> None:
    """Explain the notebook's paired circular-block algorithm without synthetic results."""
    figure, axis = plt.subplots(figsize=(11.8, 6.6))
    figure.patch.set_facecolor(BACKGROUND)
    axis.set_facecolor(BACKGROUND)
    axis.set_xlim(0, 13.2)
    axis.set_ylim(0, 8.6)
    axis.axis("off")
    add_title(
        figure,
        TEXT["scheme_title"],
        TEXT["scheme_subtitle"],
    )

    # Original series: the blocks are consecutive and wrap from the end to the beginning.
    axis.text(0.08, 7.35, TEXT["paired_heading"], color=INK, fontsize=9.2, fontweight="bold")
    axis.text(0.08, 6.95, TEXT["paired_equation"], color=WARM_GRAY, fontsize=8.5)
    add_sequence(axis, 6.15, 12, TEXT["dates"], "#CFC8BD")
    axis.text(10.8, 5.82, "...", color=WARM_GRAY, fontsize=13)
    axis.add_patch(FancyArrowPatch((10.35, 6.14), (1.65, 6.14), connectionstyle="arc3,rad=-0.38", arrowstyle="->", mutation_scale=11, color=TERRACOTTA, linewidth=1.1))
    axis.text(5.1, 5.48, TEXT["circular_note"], color=WARM_GRAY, fontsize=8.2)

    axis.text(0.08, 4.64, TEXT["selection_heading"], color=INK, fontsize=9.2, fontweight="bold")
    axis.text(0.08, 4.25, TEXT["selection_note"], color=WARM_GRAY, fontsize=8.5)
    add_sequence(axis, 3.32, 5, TEXT["block_21"], P1_COLOR, 2.3)
    axis.text(6.08, 3.58, "+", color=WARM_GRAY, fontsize=13, va="center")
    add_sequence(axis, 3.32, 5, "", "#B49A85", 6.55)
    axis.text(10.05, 3.58, TEXT["complete_note"], color=WARM_GRAY, fontsize=8.2, va="center")
    add_sequence(axis, 2.05, 8, TEXT["block_63"], P2_COLOR, 2.3)
    axis.text(8.15, 2.31, TEXT["long_block_note"], color=WARM_GRAY, fontsize=8.2, va="center")

    axis.add_patch(FancyArrowPatch((6.6, 1.76), (6.6, 1.16), arrowstyle="->", mutation_scale=12, color=TERRACOTTA, linewidth=1.1))
    axis.text(0.08, 0.67, TEXT["stat_heading"], color=INK, fontsize=9.2, fontweight="bold")
    axis.text(2.2, 0.67, TEXT["stat_note"], color=WARM_GRAY, fontsize=8.7)
    figure.subplots_adjust(left=0.06, right=0.98, top=0.87, bottom=0.07)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    figure.savefig(BOOTSTRAP_SCHEME_PATH, dpi=180, facecolor=BACKGROUND)
    plt.close(figure)


def create_intervals_figure(metrics: dict[str, dict[str, object]]) -> None:
    """Plot both bootstrap block lengths with their notebook-defined 95% intervals."""
    figure, axes = plt.subplots(1, 2, figsize=(11.8, 5.55), gridspec_kw={"wspace": 0.38})
    figure.patch.set_facecolor(BACKGROUND)
    add_title(
        figure,
        TEXT["intervals_title"],
        TEXT["intervals_subtitle"],
    )
    panel_specs = (
        (axes[0], "growth", TEXT["interval_growth_heading"], TEXT["growth_unit"], TEXT["interval_growth_note"]),
        (axes[1], "mae", TEXT["interval_mae_heading"], TEXT["mae_unit"], TEXT["interval_mae_note"]),
    )
    y_positions = {"P1": 1.0, "P2": 0.0}
    offsets = {21: 0.14, 63: -0.14}
    for axis, metric, heading, unit, note in panel_specs:
        for policy in ("P1", "P2"):
            for block in BLOCK_LENGTHS:
                result = metrics[policy][metric][block]
                y = y_positions[policy] + offsets[block]
                axis.hlines(y, result["lower"], result["upper"], color=BLOCK_COLORS[block], linewidth=2.1, zorder=2)
                axis.plot(result["point"], y, "o", color=BLOCK_COLORS[block], markersize=5.2, zorder=3)
        axis.axvline(0, color=INK, linewidth=0.9, zorder=1)
        axis.set_yticks([1.0, 0.0], ["P1 vs P0", "P2 vs P0"])
        axis.set_ylim(-0.55, 1.55)
        axis.set_title(heading, loc="left", color=INK, fontsize=9.1, fontweight="bold", pad=12)
        axis.set_xlabel(unit, color=INK, fontsize=8.5, labelpad=9)
        axis.text(0, -0.30, note, transform=axis.transAxes, color=WARM_GRAY, fontsize=8)
        style_axis(axis)
        left, right = axis.get_xlim()
        padding = (right - left) * 0.12
        axis.set_xlim(left - padding, right + padding)
        axis.xaxis.set_major_locator(MultipleLocator(0.25 if metric == "growth" else 0.1))
    handles = [
        plt.Line2D([0], [0], color=BLOCK_COLORS[21], marker="o", linewidth=2.1, markersize=5, label=TEXT["block_21_legend"]),
        plt.Line2D([0], [0], color=BLOCK_COLORS[63], marker="o", linewidth=2.1, markersize=5, label=TEXT["block_63_legend"]),
    ]
    figure.legend(handles=handles, loc="lower center", ncol=2, frameon=False, fontsize=8.2, labelcolor=INK, bbox_to_anchor=(0.5, 0.02))
    figure.subplots_adjust(left=0.12, right=0.97, top=0.78, bottom=0.25)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    figure.savefig(INTERVALS_PATH, dpi=180, facecolor=BACKGROUND)
    plt.close(figure)


def validate_metrics(metrics: dict[str, dict[str, object]]) -> None:
    """Protect the published interpretation before emitting any graphics."""
    expected = {
        "P1": {"growth": 0.573, "mae": 0.077},
        "P2": {"growth": 0.552, "mae": 0.303},
    }
    for policy, expected_values in expected.items():
        for metric, expected_value in expected_values.items():
            observed = metrics[policy][metric][21]["point"]
            if not math.isclose(observed, expected_value, rel_tol=0.0, abs_tol=0.0006):
                raise ValueError(
                    f"{policy} {metric} ({observed:.6f}) no coincide con el resultado aprobado ({expected_value:.3f})."
                )
            for block in BLOCK_LENGTHS:
                result = metrics[policy][metric][block]
                if not (math.isfinite(result["lower"]) and math.isfinite(result["upper"]) and result["lower"] <= result["upper"]):
                    raise ValueError(f"{policy} {metric}: invalid interval for block {block}.")


def main(language: str) -> None:
    configure_language(language)
    histories = load_certified_histories()
    metrics = calculate_metrics(histories)
    validate_metrics(metrics)
    create_tradeoff_figure(metrics)
    create_bootstrap_scheme_figure()
    create_intervals_figure(metrics)

    print(f"SOURCE_NOTEBOOK={NOTEBOOK}")
    print("INPUTS=certified P0/P1/P2 Parquet histories; Block 07 formulas and parameters")
    for policy in ("P1", "P2"):
        for metric in ("growth", "mae"):
            for block in BLOCK_LENGTHS:
                result = metrics[policy][metric][block]
                print(
                    f"{policy} {metric} block={block}: point={result['point']:.9f} "
                    f"ci95=[{result['lower']:.9f}, {result['upper']:.9f}]"
                )
    print(f"TRADEOFF={TRADEOFF_PATH}")
    print(f"BOOTSTRAP_SCHEME={BOOTSTRAP_SCHEME_PATH}")
    print(f"INTERVALS={INTERVALS_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--lang",
        choices=("es", "en"),
        default="es",
        help="Language for visible chart text (default: es).",
    )
    main(parser.parse_args().lang)
