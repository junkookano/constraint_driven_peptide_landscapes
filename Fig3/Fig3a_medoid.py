from __future__ import annotations

"""
Generate Fig. 3a medoid panels.

This script reproduces the capillary and parenchyma embedding panels shown in
Fig. 3a by plotting fixed, previously identified medoid coordinates on the
corresponding UMAP embeddings.

Input CSV filenames are provisional and may be updated at final submission.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def main() -> None:
    # ============================================================
    # 1) Paths
    # ============================================================
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data"
    fig_dir = base_dir / "figs"
    results_dir = base_dir / "results"

    fig_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    cap_path = data_dir / "df_capillary_pancreasFixed_umap_hdbscan_mcs50.csv"
    par_path = data_dir / "parenchyma_HDBSCAN_with_character.csv"

    if not cap_path.exists():
        raise FileNotFoundError(f"Missing input file: {cap_path}")
    if not par_path.exists():
        raise FileNotFoundError(f"Missing input file: {par_path}")

    print(f"[INFO] Capillary input: {cap_path}")
    print(f"[INFO] Parenchyma input: {par_path}")

    # ============================================================
    # 2) Load embeddings
    # ============================================================
    cap = pd.read_csv(cap_path)
    par = pd.read_csv(par_path)

    for name, df in [("capillary", cap), ("parenchyma", par)]:
        missing = [c for c in ["UMAP1", "UMAP2"] if c not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns in {name} table: {missing}")

    print(f"[INFO] Capillary rows: {len(cap)}")
    print(f"[INFO] Parenchyma rows: {len(par)}")

    # ============================================================
    # 3) Fixed medoid coordinates
    #    These medoids were identified independently upstream.
    # ============================================================
    cap_medoids = [
        ("STLHQEL", 0.149805, 6.037934),
    ]

    par_medoids = [
        ("STFHQKL", 4.664472, 11.359691),
    ]

    # ============================================================
    # 4) Shared axis limits
    # ============================================================
    all_x = np.concatenate([cap["UMAP1"].to_numpy(), par["UMAP1"].to_numpy()])
    all_y = np.concatenate([cap["UMAP2"].to_numpy(), par["UMAP2"].to_numpy()])

    pad_x = 0.03 * (all_x.max() - all_x.min())
    pad_y = 0.03 * (all_y.max() - all_y.min())

    xlim = (all_x.min() - pad_x, all_x.max() + pad_x)
    ylim = (all_y.min() - pad_y, all_y.max() + pad_y)

    # ============================================================
    # 5) Plotting function
    # ============================================================
    def panel(ax, df: pd.DataFrame, medoids: list[tuple[str, float, float]]) -> None:
        # Background points
        ax.scatter(
            df["UMAP1"],
            df["UMAP2"],
            s=6,
            alpha=0.12,
            color="lightgray",
            linewidths=0,
        )

        # Fixed medoids
        for label, x, y in medoids:
            ax.scatter(
                x,
                y,
                s=42,
                color="black",
                edgecolors="black",
                linewidths=0.6,
                zorder=5,
            )

        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel("UMAP1")
        ax.set_ylabel("UMAP2")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)

    # ============================================================
    # 6) Draw panels
    # ============================================================
    fig, axes = plt.subplots(1, 2, figsize=(7, 3.5), constrained_layout=True)

    panel(axes[0], cap, cap_medoids)
    panel(axes[1], par, par_medoids)
    axes[1].set_ylabel("")

    # ============================================================
    # 7) Save outputs
    # ============================================================
    out_svg = fig_dir / "Fig3A_cap_par_medoids.svg"
    out_png = fig_dir / "Fig3A_cap_par_medoids_600dpi.png"

    fig.savefig(out_svg, format="svg", bbox_inches="tight")
    fig.savefig(out_png, dpi=600, bbox_inches="tight")
    plt.close(fig)

    print(f"[SAVED] {out_svg}")
    print(f"[SAVED] {out_png}")


if __name__ == "__main__":
    main()