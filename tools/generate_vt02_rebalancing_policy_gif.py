"""Generate the Volatility Targeting 02 operational-policy animation.

The script executes the causal backtest cells from notebook 02 in memory. It
does not write to or alter the scientific notebook.
"""

from __future__ import annotations

import json
import os
from io import BytesIO
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from PIL import Image


SITE_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = (
    SITE_ROOT.parent
    / "quant-research-notes"
    / "volatility_target"
    / "01_rebalancing_policies"
    / "02_rebalancing_policies.ipynb"
)
OUTPUT_DIR = SITE_ROOT / "img" / "volatility_targeting" / "02_rebalancing"
GIF_PATH = OUTPUT_DIR / "rebalancing_policy_comparison.gif"
FRAME_PATH = OUTPUT_DIR / "rebalancing_policy_comparison_frame.png"
CELL_INDICES = (3, 4, 6, 9, 12, 15, 17, 20, 21, 24, 27, 29, 31)
WINDOW_START = 1056
WINDOW_SIZE = 100

BACKGROUND = "#F7F5EF"
INK = "#252522"
WARM_GRAY = "#776F65"
GRID = "#D9D3C9"
TERRACOTTA = "#A9684F"
NO_FILL = "#978B7D"


def execute_backtest() -> dict:
    """Execute only the notebook cells needed to construct P0, P1 and P2."""
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    namespace: dict[str, object] = {"__name__": "__main__"}
    original_cwd = Path.cwd()
    try:
        os.chdir(NOTEBOOK.parent)
        for index in CELL_INDICES:
            source = "".join(notebook["cells"][index]["source"])
            exec(compile(source, f"{NOTEBOOK.name}:cell-{index}", "exec"), namespace)
    finally:
        os.chdir(original_cwd)
    return namespace["policy_histories"]


def selected_window(histories: dict) -> dict[str, dict[str, list]]:
    """Return the pre-specified median-activity 100-session window."""
    panels: dict[str, dict[str, list]] = {}
    labels = {
        "P0 — Daily": "P0  ·  DAILY REBALANCING",
        "P1 — Banda 5 pp": "P1  ·  ±5 PP BAND",
        "P2 — Banda 10 pp": "P2  ·  ±10 PP BAND",
    }
    for policy, label in labels.items():
        history = histories[policy].slice(WINDOW_START, WINDOW_SIZE)
        panels[policy] = {
            "label": label,
            "dates": history["session_date"].to_list(),
            "target": history["target_weight"].to_list(),
            "effective": history["effective_weight_after"].to_list(),
            "executed": history["trade_executed"].to_list(),
            "no_fill": history["no_fill"].to_list(),
        }
    return panels


def draw_frame(panels: dict[str, dict[str, list]], endpoint: int, *, final: bool) -> Image.Image:
    """Render a progressive frame using only target, effective weight and events."""
    fig, axes = plt.subplots(
        3,
        1,
        figsize=(11.6, 8.0),
        sharex=True,
        gridspec_kw={"hspace": 0.23, "top": 0.86, "bottom": 0.11, "left": 0.10, "right": 0.96},
    )
    fig.patch.set_facecolor(BACKGROUND)
    dates = next(iter(panels.values()))["dates"]
    current_date = dates[endpoint]
    for axis, panel in zip(axes, panels.values(), strict=True):
        axis.set_facecolor(BACKGROUND)
        visible = slice(0, endpoint + 1)
        axis.plot(
            dates[visible],
            panel["target"][visible],
            color=WARM_GRAY,
            linewidth=1.35,
            linestyle=(0, (3, 2)),
            label="Target weight",
            zorder=2,
        )
        axis.plot(
            dates[visible],
            panel["effective"][visible],
            color=INK,
            linewidth=1.75,
            label="Effective weight",
            zorder=3,
        )
        event_indices = [
            index for index, executed in enumerate(panel["executed"][: endpoint + 1]) if executed
        ]
        if event_indices:
            axis.scatter(
                [dates[index] for index in event_indices],
                [panel["effective"][index] for index in event_indices],
                marker="|",
                s=92,
                linewidths=1.35,
                color=TERRACOTTA,
                label="Executed rebalance",
                zorder=5,
            )
        no_fill_indices = [
            index for index, no_fill in enumerate(panel["no_fill"][: endpoint + 1]) if no_fill
        ]
        if no_fill_indices:
            axis.scatter(
                [dates[index] for index in no_fill_indices],
                [panel["target"][index] for index in no_fill_indices],
                marker="x",
                s=24,
                linewidths=1.0,
                color=NO_FILL,
                label="No-fill",
                zorder=6,
            )
        axis.axvline(current_date, color=TERRACOTTA, alpha=0.38, linewidth=0.8, zorder=1)
        axis.set_xlim(dates[0], dates[-1])
        axis.set_ylim(0.35, 1.02)
        axis.yaxis.set_major_formatter(lambda value, position: f"{value:.0%}")
        axis.set_yticks((0.4, 0.6, 0.8, 1.0))
        axis.grid(axis="y", color=GRID, linewidth=0.65)
        axis.tick_params(axis="both", colors=WARM_GRAY, labelsize=8, length=0)
        for spine in axis.spines.values():
            spine.set_visible(False)
        axis.text(
            0.0,
            1.08,
            panel["label"],
            transform=axis.transAxes,
            color=INK,
            fontsize=8.5,
            fontfamily="DejaVu Sans Mono",
            fontweight="bold",
            va="bottom",
        )

    axes[-1].xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    axes[0].legend(
        loc="upper right",
        ncol=4,
        frameon=False,
        fontsize=7.5,
        handlelength=2.2,
        labelcolor=INK,
        borderaxespad=0.25,
    )
    fig.text(
        0.10,
        0.955,
        "VOLATILITY TARGETING  ·  OPERATIONAL POLICY RESPONSE",
        color=INK,
        fontsize=12,
        fontfamily="DejaVu Sans",
        fontweight="bold",
    )
    fig.text(
        0.10,
        0.923,
        "Same EWMA target · executed rebalances shown as vertical marks · no-fill shown as ×",
        color=WARM_GRAY,
        fontsize=8.4,
        fontfamily="DejaVu Sans",
    )
    fig.text(
        0.96,
        0.955,
        f"{current_date:%d %b %Y}  ·  {endpoint + 1:03d}/{WINDOW_SIZE}",
        ha="right",
        color=TERRACOTTA if not final else INK,
        fontsize=8.4,
        fontfamily="DejaVu Sans Mono",
    )
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=105, facecolor=BACKGROUND)
    plt.close(fig)
    buffer.seek(0)
    return Image.open(buffer).convert("P", palette=Image.Palette.ADAPTIVE, colors=128)


def main() -> None:
    histories = execute_backtest()
    panels = selected_window(histories)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    frames = [draw_frame(panels, endpoint, final=False) for endpoint in range(WINDOW_SIZE)]
    frames[-1].save(FRAME_PATH, format="PNG")
    frames[0].save(
        GIF_PATH,
        format="GIF",
        append_images=frames[1:],
        save_all=True,
        duration=110,
        loop=0,
        optimize=True,
        disposal=2,
    )
    p0 = panels["P0 — Daily"]
    p1 = panels["P1 — Banda 5 pp"]
    p2 = panels["P2 — Banda 10 pp"]
    print(f"PERIOD={p0['dates'][0]} to {p0['dates'][-1]}")
    print(f"TARGET_RANGE={max(p0['target']) - min(p0['target']):.6f}")
    print(f"P0_EXECUTED={sum(p0['executed'])} P1_EXECUTED={sum(p1['executed'])} P2_EXECUTED={sum(p2['executed'])}")
    print(f"P0_NO_FILL={sum(p0['no_fill'])} P1_NO_FILL={sum(p1['no_fill'])} P2_NO_FILL={sum(p2['no_fill'])}")
    print(f"GIF={GIF_PATH}")
    print(f"FRAME={FRAME_PATH}")


if __name__ == "__main__":
    main()
