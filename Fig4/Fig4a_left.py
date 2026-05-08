from __future__ import annotations

"""
Generate Fig. 4a left panel.

This script reproduces the left-side UMAP panel shown in Fig. 4a by plotting
fixed coordinates for STLHQEL, STFHQKL, and EVGTARY on the global embedding.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def main() -> None:
    # ============================================================
    # 1) Paths
    # ============================================================
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data"
    fig_dir = base_dir / "figs"

    fig_dir.mkdir(parents=True, exist_ok=True)

    csv_path = data_dir / "merged_cap_par_CPM.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing input file: {csv_path}")

    print(f"[INFO] Input CSV: {csv_path}")

    # ============================================================
    # 2) Load embedding table
    # ============================================================
    df = pd.read_csv(csv_path)

    required_cols = ["UMAP1", "UMAP2"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    print(f"[INFO] Input rows: {len(df)}")

    # ============================================================
    # 3) Colors
    # ============================================================
    gray_bg = "#D9D9D9"
    blue_stl = "#4DBBD5"       # STLHQEL
    orange_stf = "#E64B35"     # STFHQKL
    turquoise_evg = "#00A087"  # EVGTARY

    # ============================================================
    # 4) Fixed points
    # ============================================================
    pts = [
        ("STLHQEL", 0.149805, 6.037934, blue_stl),
        ("STFHQKL", 4.664472, 11.359691, orange_stf),
        ("EVGTARY", 14.586409, 22.578264, turquoise_evg),
    ]

    # ============================================================
    # 5) Plot
    # ============================================================
    fig, ax = plt.subplots(figsize=(6, 6))

    # background
    ax.scatter(
        df["UMAP1"],
        df["UMAP2"],
        s=6,
        color=gray_bg,
        alpha=0.20,
        linewidths=0,
    )

    # highlighted fixed points
    for label, x, y, col in pts:
        if label == "EVGTARY":
            size = 50
            lw = 1.0
            z = 4
        else:
            size = 20
            lw = 0.7
            z = 3

        ax.scatter(
            x,
            y,
            s=size,
            color=col,
            edgecolor="#333333",
            linewidth=lw,
            zorder=z,
        )

        ax.text(
            x + 0.3,
            y + 0.7,
            label,
            fontsize=9,
            color=col,
            ha="left",
            va="bottom",
            weight="bold",
        )

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.grid(False)
    ax.set_aspect("equal", adjustable="box")

    plt.tight_layout()

    # ============================================================
    # 6) Save
    # ============================================================
    stem = "Fig4A_left_global_UMAP_fixed_points"
    out_svg = fig_dir / f"{stem}.svg"
    out_png = fig_dir / f"{stem}_600dpi.png"

    fig.savefig(out_svg, format="svg", bbox_inches="tight")
    fig.savefig(out_png, dpi=600, bbox_inches="tight")
    plt.close(fig)

    print(f"[SAVED] {out_svg}")
    print(f"[SAVED] {out_png}")


if __name__ == "__main__":
    main()