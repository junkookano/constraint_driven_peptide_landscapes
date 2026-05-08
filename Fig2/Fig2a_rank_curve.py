from __future__ import annotations

"""
Generate Fig. 2a digital subtraction rank curve.

This script reproduces the visualization shown in Fig. 2a from the processed
bulk R1/R3 digital subtraction table.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


def main() -> None:
    # ============================================================
    # 1) Paths
    # ============================================================
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data"
    fig_dir = base_dir / "figs"

    fig_dir.mkdir(parents=True, exist_ok=True)

    csv_path = data_dir / "bulk_R1R3_enrichment_Fig2_input_top3000.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing input file: {csv_path}")

    print(f"[INFO] Input CSV: {csv_path}")

    # ============================================================
    # 2) Load table
    # ============================================================
    df = pd.read_csv(csv_path)
    print(f"[INFO] Input rows: {len(df)}")

    required_cols = ["subtraction_score", "E_max_other"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(
            f"Missing required columns in CSV: {missing}. "
            f"Found columns: {list(df.columns)[:20]} ..."
        )

    # ============================================================
    # 3) Rank table
    # ============================================================
    rank_cols = ["subtraction_score", "E_max_other"]
    if "character" in df.columns:
        rank_cols.append("character")

    df_rank = (
        df[rank_cols]
        .sort_values("subtraction_score", ascending=False)
        .reset_index(drop=True)
    )
    df_rank["rank"] = np.arange(1, len(df_rank) + 1)

    # Shared is defined strictly as E_max_other > 0
    is_shared = (df_rank["E_max_other"] > 0).to_numpy()
    is_exclusive = ~is_shared

    if is_shared.any():
        first_shared_rank = int(np.argmax(is_shared) + 1)  # 1-based
    else:
        first_shared_rank = None

    print(f"[INFO] First shared rank: {first_shared_rank}")

    # ============================================================
    # 4) Plot settings
    # ============================================================
    n_main = min(3000, len(df_rank))
    inset_xl, inset_xr = 120, 240
    point_size_main = 8
    point_size_inset = 12

    x = df_rank["rank"].iloc[:n_main].to_numpy()
    y = df_rank["subtraction_score"].iloc[:n_main].to_numpy()
    shared_main = is_shared[:n_main]
    exclusive_main = ~shared_main

    # ============================================================
    # 5) Main plot
    # ============================================================
    fig, ax = plt.subplots(figsize=(7.2, 4.6), constrained_layout=True)

    ax.scatter(
        x[exclusive_main],
        y[exclusive_main],
        s=point_size_main,
        alpha=0.9,
        label="cerebrum-exclusive (E_max_other = 0)",
    )
    ax.scatter(
        x[shared_main],
        y[shared_main],
        s=point_size_main,
        alpha=0.9,
        label="shared (E_max_other > 0)",
    )

    if first_shared_rank is not None and first_shared_rank <= n_main:
        ax.axvline(
            first_shared_rank,
            linestyle="--",
            linewidth=1.2,
            color="red",
            alpha=0.85,
        )
        ax.text(
            first_shared_rank + 20,
            float(np.max(y)),
            f"first shared (rank {first_shared_rank})",
            color="red",
            fontsize=9,
            va="top",
        )

    ax.set_xlabel(f"Rank (1–{n_main}, sorted by subtraction_score)")
    ax.set_ylabel("subtraction_score")
    ax.set_xlim(1, n_main)
    ax.legend(frameon=False, fontsize=9, loc="upper right")

    # ============================================================
    # 6) Inset
    # ============================================================
    axins = inset_axes(
        ax,
        width="30%",
        height="40%",
        bbox_to_anchor=(0.55, 0.35, 1, 1),
        bbox_transform=ax.transAxes,
        loc="lower left",
        borderpad=0,
    )

    xl = max(1, inset_xl)
    xr = min(n_main, inset_xr)
    mask_inset = (x >= xl) & (x <= xr)

    x_i = x[mask_inset]
    y_i = y[mask_inset]
    shared_i = shared_main[mask_inset]
    exclusive_i = ~shared_i

    axins.scatter(x_i[exclusive_i], y_i[exclusive_i], s=point_size_inset, alpha=0.95)
    axins.scatter(x_i[shared_i], y_i[shared_i], s=point_size_inset, alpha=0.95)

    if first_shared_rank is not None and (xl <= first_shared_rank <= xr):
        axins.axvline(
            first_shared_rank,
            linestyle="--",
            linewidth=1.0,
            color="red",
            alpha=0.85,
        )

    axins.set_xlim(xl, xr)

    if len(y_i) > 0:
        ymin = float(np.min(y_i))
        ymax = float(np.max(y_i))
        pad = (ymax - ymin) * 0.08 if ymax > ymin else 0.2
        axins.set_ylim(ymin - pad, ymax + pad)

    axins.set_title(f"Transition region: ranks {xl}–{xr}", fontsize=9)
    axins.tick_params(labelsize=8)

   

    # ============================================================
    # 7) Save outputs
    # ============================================================
    stem = "Fig2A_digital_subtraction_rankcurve_bulk_R1R3"
    out_svg = fig_dir / f"{stem}.svg"
    out_png = fig_dir / f"{stem}_600dpi.png"

    fig.savefig(out_svg, format="svg", bbox_inches="tight")
    fig.savefig(out_png, dpi=600, bbox_inches="tight")
    plt.close(fig)

    print(f"[SAVED] {out_svg}")
    print(f"[SAVED] {out_png}")


if __name__ == "__main__":
    main()