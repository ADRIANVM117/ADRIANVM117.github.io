"""Regenerate the certified Factor Momentum 02 execution visuals.

This is a presentation-only consumer of the audited research implementation.
It executes the minimum required notebook cells in memory, pins the signal
comparison to P0, validates Gold hashes and published controls, then writes
only public image assets under img/factor_momentum/02_xle_execution/.

It never writes to quant-research-notes, its Gold inputs, or any notebook.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import date as calendar_date
from hashlib import sha256
from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.ticker import StrMethodFormatter
from PIL import Image


P0_COMMIT = "af9a5f44412cc940fc655af92f74669fe341e84b"
P0_SIGNAL_SHA256 = "5c43aa1b60930b4f16d6e60e13f818ca1a3ae23569ec64a4cf96adc1b0c97c5e"
EXPECTED_GOLD_HASHES = {
    "SPY": "b0767b45c2d67dbe8d99e11e1603682fd28468c31de65d037a4c0a50fefa67e9",
    "IWM": "7913707e8a33b60780a7fe93617eb8114ef71b0e66e6a3b0b4dbab752cf09523",
    "IWD": "d73576d8c83dcbe57392174cb341061321ab963cd4adbdd063f455342caea0e0",
    "IWF": "d0c4165277bc9167421dde15ef9ede395bc35d259326de22913a76ef5792314e",
    "XLE": "f98e7468b5aee758298229a14443818ea0148bc46b26042a02abe1dee9af7a5a",
}
REFERENCE_SCENARIO = "IBKR Pro Fixed + 5 bps"
INITIAL_CAPITAL = 10_000.0
OUTPUT_NAMES = {
    "gif": "systematic_vs_buyhold_nav.gif",
    "frame": "systematic_vs_buyhold_nav_final_frame.png",
    "comparison": "xle_strategy_nav_comparison.png",
    "slippage": "xle_slippage_sensitivity.png",
}
COLORS = {
    "Systematic momentum": "#252522",
    "Buy & Hold": "#9a604b",
    "TSMOM total": "#7b756d",
    "Market momentum": "#b08a72",
}
IVORY = "#f7f5ef"
GRID = "#d8d2c8"
MUTED = "#716b63"
VISUAL_TEXT = {
    "es": {
        "gif_title": "XLE — patrimonio simulado bajo ejecución operativa",
        "execution_subtitle": "IBKR Pro Fixed + slippage adverso ilustrativo de 5 bps · carteras simuladas",
        "portfolio_value": "Patrimonio (USD)",
        "comparison_title": "XLE — NAV operativo de cuatro estrategias",
        "slippage_title": "XLE — sensibilidad del CAGR al slippage supuesto",
        "slippage_subtitle": "Systematic Momentum · comisiones IBKR Pro Fixed en todos los escenarios · carteras simuladas",
        "cagr": "CAGR anualizado (%)",
        "slippage_note": "bps = slippage adverso supuesto; no representa un costo observado.",
    },
    "en": {
        "gif_title": "XLE — simulated wealth under operational execution",
        "execution_subtitle": "IBKR Pro Fixed + 5 bps assumed adverse slippage · simulated portfolios",
        "portfolio_value": "Portfolio value (USD)",
        "comparison_title": "XLE — operational NAV across four strategies",
        "slippage_title": "XLE — CAGR sensitivity to assumed slippage",
        "slippage_subtitle": "Systematic Momentum · IBKR Pro Fixed commissions in every scenario · simulated portfolios",
        "cagr": "Annualized CAGR (%)",
        "slippage_note": "bps = assumed adverse slippage; not an observed cost.",
    },
}


def notebook_code(notebook: dict[str, Any], cell_id: str) -> str:
    for cell in notebook["cells"]:
        if cell.get("id") == cell_id:
            return "".join(cell["source"])
    raise RuntimeError(f"Required notebook cell is missing: {cell_id}")


def read_notebook(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def project_roots(scientific_root_arg: str | None) -> tuple[Path, Path, Path]:
    site_root = Path(__file__).resolve().parents[1]
    scientific_root = (
        Path(scientific_root_arg).resolve()
        if scientific_root_arg
        else site_root.parent / "quant-research-notes" / "Momentum_systematic_strategies"
    )
    if not (scientific_root / "02_factor_momentum").is_dir():
        raise FileNotFoundError(
            "No Factor Momentum scientific root was found. Pass --scientific-root "
            "pointing at Momentum_systematic_strategies."
        )
    return site_root, scientific_root, scientific_root.parent


def validate_gold(scientific_root: Path) -> None:
    gold_root = scientific_root / "data" / "gold" / "daily_series" / "etf"
    for symbol, expected_hash in EXPECTED_GOLD_HASHES.items():
        path = gold_root / f"{symbol}.parquet"
        if not path.is_file():
            raise FileNotFoundError(f"Missing audited Gold input: {path}")
        observed_hash = sha256_file(path)
        if observed_hash != expected_hash:
            raise RuntimeError(
                f"{symbol} Gold hash mismatch: {observed_hash}; expected {expected_hash}."
            )


def p0_signal_notebook(repository_root: Path) -> dict[str, Any]:
    spec = (
        f"{P0_COMMIT}:Momentum_systematic_strategies/02_factor_momentum/"
        "notebooks/02_factor_momentum_signal_test.ipynb"
    )
    try:
        payload = subprocess.check_output(
            ["git", "-C", str(repository_root), "show", spec], text=False
        )
    except subprocess.CalledProcessError as error:
        raise RuntimeError(
            f"The pinned P0 revision {P0_COMMIT} is unavailable in the local clone."
        ) from error
    observed_hash = sha256(payload).hexdigest()
    if observed_hash != P0_SIGNAL_SHA256:
        raise RuntimeError(
            f"P0 signal hash mismatch: {observed_hash}; expected {P0_SIGNAL_SHA256}."
        )
    return json.loads(payload.decode("utf-8"))


def execute_certified_series(scientific_root: Path, repository_root: Path) -> dict[str, Any]:
    """Recover existing ledgers through the audited execution implementation."""
    validate_gold(scientific_root)
    execution_path = (
        scientific_root
        / "02_factor_momentum"
        / "strategy_candidates"
        / "xle_systematic_momentum"
        / "notebooks"
        / "01_execution_feasibility.ipynb"
    )
    if not execution_path.is_file():
        raise FileNotFoundError(f"Execution notebook is missing: {execution_path}")

    execution_notebook = read_notebook(execution_path)
    p0_notebook = p0_signal_notebook(repository_root)
    original_cwd = Path.cwd()
    try:
        os.chdir(scientific_root)
        state: dict[str, Any] = {"__name__": "__fm02_execution_visuals__"}
        for cell_id in ("imports-and-gold", "rebuild-frozen-signals"):
            exec(compile(notebook_code(execution_notebook, cell_id), str(execution_path), "exec"), state)

        # P1 pins the comparison reference to this exact P0 source. Execute it
        # separately in memory so no local scientific file is replaced.
        reference_state: dict[str, Any] = {"__name__": "__fm02_p0_reference__"}
        for cell_id in (
            "imports-and-data",
            "returns-and-oos-attribution",
            "signal-construction",
            "strategy-returns",
        ):
            exec(compile(notebook_code(p0_notebook, cell_id), "P0_signal.ipynb", "exec"), reference_state)

        schedule = state["execution_schedule"]
        candidate_weights = pl.concat(
            [
                schedule.select(
                    "signal_date", "return_date", pl.lit("TSMOM total").alias("alternative"),
                    pl.col("tsmom_weight").alias("weight"),
                ),
                schedule.select(
                    "signal_date", "return_date", pl.lit("Market momentum").alias("alternative"),
                    pl.col("market_weight").alias("weight"),
                ),
                schedule.select(
                    "signal_date", "return_date", pl.lit("Systematic momentum").alias("alternative"),
                    pl.col("systematic_weight").alias("weight"),
                ),
            ]
        )
        reference_weights = (
            reference_state["strategy_returns"]
            .filter(
                (pl.col("asset") == "XLE")
                & pl.col("alternative").is_in(
                    ["TSMOM total", "Market momentum", "Systematic momentum"]
                )
            )
            .select("signal_date", "return_date", "alternative", "weight")
        )
        signal_check = candidate_weights.join(
            reference_weights,
            on=["signal_date", "return_date", "alternative"],
            how="inner",
            suffix="_p0",
        )
        max_difference = float((signal_check["weight"] - signal_check["weight_p0"]).abs().max())
        if signal_check.height != 5559 or max_difference != 0.0:
            raise RuntimeError(
                "The execution schedule does not exactly reproduce the P0 signal "
                f"(rows={signal_check.height}, max difference={max_difference})."
            )

        for cell_id in ("execution-engine", "run-scenarios", "execution-summary"):
            exec(compile(notebook_code(execution_notebook, cell_id), str(execution_path), "exec"), state)
    finally:
        os.chdir(original_cwd)

    summary = state["execution_summary"]
    ledger = state["ledger"]
    operations = state["operations"]
    expected_reference = {
        "final_capital": 28028.02,
        "cagr_pct": 15.046,
        "sharpe": 0.618,
        "max_drawdown_pct": -27.805,
        "operations": 63,
        "commission_total": 68.23,
        "slippage_total": 455.95,
    }
    reference_row = (
        summary.filter(
            (pl.col("scenario") == REFERENCE_SCENARIO)
            & (pl.col("strategy") == "Systematic momentum")
        )
        .to_dicts()
    )
    if len(reference_row) != 1:
        raise RuntimeError("Missing Systematic Momentum reference scenario.")
    reference_row = reference_row[0]
    for key, expected in expected_reference.items():
        actual = reference_row[key]
        tolerance = 0 if key == "operations" else 0.01
        if abs(actual - expected) > tolerance:
            raise RuntimeError(f"Reference control failed for {key}: {actual}; expected {expected}.")

    fixed_ledgers = ledger.filter(pl.col("scenario") == REFERENCE_SCENARIO)
    date_counts = fixed_ledgers.group_by("strategy").agg(pl.col("date").n_unique().alias("n_dates"))
    if set(date_counts["n_dates"].to_list()) != {1853}:
        raise RuntimeError("Fixed + 5 bps strategies do not share the 1,853-session calendar.")
    schedule = state["execution_schedule"]
    if schedule.height != 1853:
        raise RuntimeError(f"Execution schedule has {schedule.height} rows; expected 1,853.")
    dividend_events = schedule.filter(pl.col("dividend_amount").fill_null(0) != 0).height
    split_events = schedule.filter(pl.col("split_coefficient").fill_null(1) != 1).height
    if dividend_events != 30 or split_events != 1:
        raise RuntimeError(
            "Execution-schedule corporate-action controls failed "
            f"(dividends={dividend_events}, splits={split_events})."
        )

    expected_final_capital = {
        "Systematic momentum": 28028.02,
        "TSMOM total": 13276.06,
        "Market momentum": 22745.17,
        "Buy & Hold": 23494.51,
    }
    for strategy, expected in expected_final_capital.items():
        nav = (
            fixed_ledgers.filter(pl.col("strategy") == strategy)
            .sort("date")
            .get_column("nav")
        )
        if abs(float(nav[-1]) - expected) > 0.01:
            raise RuntimeError(f"Terminal NAV failed for {strategy}: {nav[-1]}; expected {expected}.")

    # Same fixed-commission execution engine as the pre-paper friction review.
    friction_rows: list[dict[str, float]] = []
    for bps in (0.0, 5.0, 10.0, 20.0):
        scenario = f"Visual review fixed + {bps:g} bps"
        state["SCENARIOS"][scenario] = {"commission": True, "slippage_bps": bps}
        history, trades = state["run_execution"](state["execution_schedule"], "Systematic momentum", scenario)
        nav = history.get_column("nav").to_numpy()
        log_returns = np.diff(np.log(np.r_[INITIAL_CAPITAL, nav]))
        friction_rows.append(
            {
                "slippage_bps": bps,
                "final_capital": float(nav[-1]),
                "cagr_pct": float(((nav[-1] / INITIAL_CAPITAL) ** (252 / len(log_returns)) - 1) * 100),
                "operations": float(trades.height),
            }
        )
    expected_friction = {
        0.0: (28919.01, 15.536),
        5.0: (28028.02, 15.046),
        10.0: (27208.97, 14.583),
        20.0: (25522.49, 13.590),
    }
    for row in friction_rows:
        capital, cagr = expected_friction[row["slippage_bps"]]
        if abs(row["final_capital"] - capital) > 0.01 or abs(row["cagr_pct"] - cagr) > 0.001:
            raise RuntimeError(f"Slippage control failed at {row['slippage_bps']:g} bps.")

    return {
        "ledger": fixed_ledgers,
        "operations": operations.filter(pl.col("scenario") == REFERENCE_SCENARIO),
        "summary": summary.filter(pl.col("scenario") == REFERENCE_SCENARIO),
        "friction": friction_rows,
        "signal_rows": signal_check.height,
        "signal_max_difference": max_difference,
        "schedule_start": str(schedule.get_column("return_date").min()),
        "schedule_end": str(schedule.get_column("return_date").max()),
        "dividend_events": dividend_events,
        "split_events": split_events,
        "execution_notebook_sha256": sha256_file(execution_path),
    }


def configure_axis(axis: plt.Axes, title: str, subtitle: str, maximum: float) -> None:
    axis.set_facecolor(IVORY)
    axis.set_title(title, loc="left", fontsize=17, fontweight="normal", color="#252522", pad=30)
    axis.text(
        0,
        1.015,
        subtitle,
        transform=axis.transAxes,
        ha="left",
        va="bottom",
        fontsize=9.5,
        color=MUTED,
    )
    axis.set_ylim(0, maximum)
    axis.yaxis.set_major_formatter(StrMethodFormatter("${x:,.0f}"))
    axis.grid(axis="y", color=GRID, linewidth=0.7)
    axis.spines[["top", "right"]].set_visible(False)
    axis.spines[["left", "bottom"]].set_color(GRID)
    axis.tick_params(colors=MUTED, labelsize=9)
    axis.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=5, maxticks=8))
    axis.xaxis.set_major_formatter(mdates.ConciseDateFormatter(axis.xaxis.get_major_locator()))


def nav_arrays(ledger: pl.DataFrame, strategy: str) -> tuple[np.ndarray, np.ndarray]:
    history = ledger.filter(pl.col("strategy") == strategy).sort("date")
    return (
        np.asarray(history.get_column("date").to_list(), dtype="datetime64[D]"),
        history.get_column("nav").to_numpy(),
    )


def render_gif_frame(
    dates: np.ndarray,
    systematic: np.ndarray,
    buy_hold: np.ndarray,
    frame_index: int,
    maximum: float,
    show_final_values: bool,
    text: dict[str, str],
    lang: str,
) -> tuple[plt.Figure, plt.Axes]:
    fig, axis = plt.subplots(figsize=(10, 6.5), dpi=140, facecolor=IVORY)
    configure_axis(
        axis,
        text["gif_title"],
        text["execution_subtitle"],
        maximum,
    )
    axis.set_xlim(dates[0], dates[-1])
    endpoint = frame_index + 1
    axis.plot(dates[:endpoint], systematic[:endpoint], color=COLORS["Systematic momentum"], linewidth=2.2, label="Systematic Momentum")
    axis.plot(dates[:endpoint], buy_hold[:endpoint], color=COLORS["Buy & Hold"], linewidth=2.0, label="Buy & Hold XLE")
    axis.axvline(dates[frame_index], color="#b08a72", linewidth=1.05, alpha=0.9)
    axis.text(
        0.995,
        0.02,
        format_visible_date(dates[frame_index], lang),
        transform=axis.transAxes,
        ha="right",
        va="bottom",
        fontsize=9,
        color=MUTED,
    )
    if show_final_values:
        for value, label, color, offset in (
            (systematic[-1], "Systematic Momentum", COLORS["Systematic momentum"], 10),
            (buy_hold[-1], "Buy & Hold XLE", COLORS["Buy & Hold"], -14),
        ):
            axis.annotate(
                f"{label}: ${value:,.2f}",
                xy=(dates[-1], value),
                xytext=(-8, offset),
                textcoords="offset points",
                ha="right",
                color=color,
                fontsize=9,
                fontweight="medium",
            )
    axis.legend(loc="upper left", bbox_to_anchor=(0, 1.0), ncol=2, frameon=False, fontsize=9)
    axis.set_ylabel(text["portfolio_value"], color=MUTED, fontsize=10)
    fig.subplots_adjust(left=0.12, right=0.96, bottom=0.13, top=0.82)
    return fig, axis


def format_visible_date(date: np.datetime64, lang: str) -> str:
    value = np.datetime_as_string(date, unit="D")
    if lang == "es":
        return value
    visible_date = calendar_date.fromisoformat(value)
    return f"{visible_date.strftime('%b')} {visible_date.day}, {visible_date.year}"


def export_nav_gif(
    ledger: pl.DataFrame, output_dir: Path, text: dict[str, str], lang: str
) -> dict[str, Any]:
    dates, systematic = nav_arrays(ledger, "Systematic momentum")
    _, buy_hold = nav_arrays(ledger, "Buy & Hold")
    frame_indices = np.unique(np.rint(np.linspace(0, len(dates) - 1, 111)).astype(int))
    if len(frame_indices) != 111 or frame_indices[-1] != len(dates) - 1:
        raise RuntimeError("GIF frame selection lost a certified ledger date.")
    maximum = float(np.ceil(max(systematic.max(), buy_hold.max()) / 5_000) * 5_000)
    gif_path = output_dir / OUTPUT_NAMES["gif"]
    frame_path = output_dir / OUTPUT_NAMES["frame"]

    figure, axis = render_gif_frame(
        dates, systematic, buy_hold, int(frame_indices[0]), maximum, False, text, lang
    )
    # Reuse the initial artists; each animation frame replaces their data, so no
    # future segment is present before the shared cursor reaches that session.
    systematic_line, buy_hold_line, cursor = axis.lines[:3]
    date_label = axis.texts[-1]

    def update(frame_number: int):
        endpoint = int(frame_indices[frame_number]) + 1
        systematic_line.set_data(dates[:endpoint], systematic[:endpoint])
        buy_hold_line.set_data(dates[:endpoint], buy_hold[:endpoint])
        cursor.set_xdata([dates[endpoint - 1], dates[endpoint - 1]])
        date_label.set_text(format_visible_date(dates[endpoint - 1], lang))
        return systematic_line, buy_hold_line, cursor, date_label

    animation = FuncAnimation(figure, update, frames=len(frame_indices), interval=125, blit=True)
    animation.save(gif_path, writer=PillowWriter(fps=8))
    plt.close(figure)

    final_figure, _ = render_gif_frame(
        dates, systematic, buy_hold, int(frame_indices[-1]), maximum, True, text, lang
    )
    final_figure.savefig(frame_path, dpi=160, facecolor=IVORY)
    plt.close(final_figure)
    with Image.open(gif_path) as gif:
        frames = gif.n_frames
        duration_ms = gif.info.get("duration", 0)
        size = gif.size
    if frames != 111:
        raise RuntimeError(f"GIF export has {frames} frames; expected 111.")
    return {"frames": frames, "duration_seconds": frames * duration_ms / 1000, "size": size}


def export_strategy_comparison(
    ledger: pl.DataFrame, output_dir: Path, text: dict[str, str]
) -> Path:
    strategies = ("Systematic momentum", "TSMOM total", "Market momentum", "Buy & Hold")
    series = {strategy: nav_arrays(ledger, strategy) for strategy in strategies}
    maximum = float(np.ceil(max(values[1].max() for values in series.values()) / 5_000) * 5_000)
    fig, axis = plt.subplots(figsize=(10, 6.5), dpi=160, facecolor=IVORY)
    configure_axis(
        axis,
        text["comparison_title"],
        text["execution_subtitle"],
        maximum,
    )
    for strategy in strategies:
        dates, nav = series[strategy]
        label = {"Systematic momentum": "Systematic Momentum", "TSMOM total": "TSMOM", "Market momentum": "Market Momentum", "Buy & Hold": "Buy & Hold XLE"}[strategy]
        axis.plot(dates, nav, label=label, color=COLORS[strategy], linewidth=2.25 if strategy == "Systematic momentum" else 1.75)
    dates = series["Systematic momentum"][0]
    axis.set_xlim(dates[0], dates[-1])
    axis.set_ylabel(text["portfolio_value"], color=MUTED, fontsize=10)
    axis.legend(loc="upper left", bbox_to_anchor=(0, 1.0), ncol=2, frameon=False, fontsize=9)
    fig.subplots_adjust(left=0.12, right=0.96, bottom=0.13, top=0.82)
    path = output_dir / OUTPUT_NAMES["comparison"]
    fig.savefig(path, dpi=160, facecolor=IVORY)
    plt.close(fig)
    return path


def export_slippage_sensitivity(
    friction: list[dict[str, float]], output_dir: Path, text: dict[str, str]
) -> Path:
    bps = np.asarray([row["slippage_bps"] for row in friction])
    cagr = np.asarray([row["cagr_pct"] for row in friction])
    colors = ["#a7a097", "#9a604b", "#a7a097", "#a7a097"]
    fig, axis = plt.subplots(figsize=(10, 6.5), dpi=160, facecolor=IVORY)
    axis.set_facecolor(IVORY)
    bars = axis.bar(np.arange(len(bps)), cagr, width=0.62, color=colors)
    axis.set_title(text["slippage_title"], loc="left", fontsize=17, color="#252522", pad=30)
    axis.text(
        0,
        1.015,
        text["slippage_subtitle"],
        transform=axis.transAxes,
        ha="left",
        va="bottom",
        fontsize=9.5,
        color=MUTED,
    )
    axis.set_xticks(np.arange(len(bps)), [f"{int(value)} bps" for value in bps])
    axis.set_ylabel(text["cagr"], color=MUTED, fontsize=10)
    axis.set_ylim(0, 17)
    axis.grid(axis="y", color=GRID, linewidth=0.7)
    axis.spines[["top", "right"]].set_visible(False)
    axis.spines[["left", "bottom"]].set_color(GRID)
    axis.tick_params(colors=MUTED, labelsize=10)
    for bar, row in zip(bars, friction, strict=True):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.24,
            f"{row['cagr_pct']:.3f}%\n${row['final_capital']:,.2f}",
            ha="center",
            va="bottom",
            color="#252522",
            fontsize=9.5,
        )
    axis.text(
        0.5,
        -0.18,
        text["slippage_note"],
        transform=axis.transAxes,
        ha="center",
        va="top",
        fontsize=9,
        color=MUTED,
    )
    fig.subplots_adjust(left=0.12, right=0.96, bottom=0.19, top=0.82)
    path = output_dir / OUTPUT_NAMES["slippage"]
    fig.savefig(path, dpi=160, facecolor=IVORY)
    plt.close(fig)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scientific-root",
        help="Path to quant-research-notes/Momentum_systematic_strategies.",
    )
    parser.add_argument(
        "--lang", choices=("es", "en"), default="es", help="Language for visible chart text."
    )
    args = parser.parse_args()
    site_root, scientific_root, repository_root = project_roots(args.scientific_root)
    output_dir = site_root / "img" / "factor_momentum" / "02_xle_execution"
    if args.lang == "en":
        output_dir /= "en"
    output_dir.mkdir(parents=True, exist_ok=True)
    text = VISUAL_TEXT[args.lang]

    evidence = execute_certified_series(scientific_root, repository_root)
    gif_info = export_nav_gif(evidence["ledger"], output_dir, text, args.lang)
    comparison_path = export_strategy_comparison(evidence["ledger"], output_dir, text)
    slippage_path = export_slippage_sensitivity(evidence["friction"], output_dir, text)

    print("PASS — P0 signal audit:", evidence["signal_rows"], "rows; max weight difference", evidence["signal_max_difference"])
    print("PASS — reference scenario: $28,028.02 | 15.046% CAGR | 0.618 Sharpe | -27.805% max drawdown | 63 operations")
    print("PASS — execution calendar:", evidence["schedule_start"], "to", evidence["schedule_end"], "| 30 dividend events | 1 split")
    print("PASS — GIF:", output_dir / OUTPUT_NAMES["gif"], f"{gif_info['frames']} frames", f"{gif_info['duration_seconds']:.3f}s", gif_info["size"])
    print("PASS — final frame:", output_dir / OUTPUT_NAMES["frame"])
    print("PASS — strategy comparison:", comparison_path)
    print("PASS — slippage sensitivity:", slippage_path)
    print("SOURCE — execution notebook SHA-256:", evidence["execution_notebook_sha256"])


if __name__ == "__main__":
    main()
