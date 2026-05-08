from __future__ import annotations

"""
Generate Fig. 4a right panel.

This script reproduces the right-side panel of Fig. 4a by identifying the
HDBSCAN cluster containing EVGTARY in the nervous-system embedding and plotting
EVGTARY together with the cluster medoid.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist


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

    csv_path = data_dir / "nervous_umap_hdbscan_mcs50.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing input file: {csv_path}")

    print(f"[INFO] Input CSV: {csv_path}")

    # ============================================================
    # 2) Load table
    # ============================================================
    df = pd.read_csv(csv_path)

    required_cols = ["UMAP1", "UMAP2", "cluster", "peptide"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    if "EVGTARY" not in set(df["peptide"]):
        raise ValueError("EVGTARY not found in dataset.")

    print(f"[INFO] Input rows: {len(df)}")

    # ============================================================
    # 3) Find EVGTARY cluster
    # ============================================================
    cluster_id = df.loc[df["peptide"] == "EVGTARY", "cluster"].iloc[0]
    df_cluster = df[df["cluster"] == cluster_id].copy()

    print(f"[INFO] EVGTARY cluster ID: {cluster_id}")
    print(f"[INFO] Cluster size: {len(df_cluster)}")

    # ============================================================
    # 4) Compute medoid within EVGTARY cluster
    # ============================================================
    x = df_cluster[["UMAP1", "UMAP2"]].to_numpy()
    dist = cdist(x, x, metric="euclidean")
    medoid_local_idx = np.argmin(dist.sum(axis=1))
    row_medoid = df_cluster.iloc[medoid_local_idx]

    medoid_x = row_medoid["UMAP1"]
    medoid_y = row_medoid["UMAP2"]
    medoid_peptide = row_medoid["peptide"]

    print(f"[INFO] Cluster medoid peptide: {medoid_peptide}")

    ev_rows = df_cluster[df_cluster["peptide"] == "EVGTARY"]
    if len(ev_rows) != 1:
        raise ValueError(f"Expected exactly one EVGTARY row, got {len(ev_rows)}")

    row_ev = ev_rows.iloc[0]
    ev_x = row_ev["UMAP1"]
    ev_y = row_ev["UMAP2"]

    # ============================================================
    # 5) Plot
    # ============================================================
    fig, ax = plt.subplots(figsize=(6, 6), dpi=600)

    # background points
    ax.scatter(
        df_cluster["UMAP1"],
        df_cluster["UMAP2"],
        s=8,
        c="#DDDDDD",
        alpha=0.8,
        edgecolor="none",
        linewidths=0,
        zorder=1,
    )

    # EVGTARY: green outline
    ax.scatter(
        ev_x,
        ev_y,
        s=40,
        facecolors="none",
        edgecolors="#00A087",
        linewidths=1.8,
        marker="o",
        zorder=8,
    )

    # Medoid: black outline
    ax.scatter(
        medoid_x,
        medoid_y,
        s=30,
        facecolors="none",
        edgecolors="#2D2D2D",
        linewidths=1.8,
        marker="o",
        zorder=7,
    )

    # ============================================================
    # 6) Square plotting window
    # ============================================================
    xvals = df_cluster["UMAP1"].to_numpy()
    yvals = df_cluster["UMAP2"].to_numpy()

    x_min, x_max = xvals.min(), xvals.max()
    y_min, y_max = yvals.min(), yvals.max()

    x_center = 0.5 * (x_min + x_max)
    y_center = 0.5 * (y_min + y_max)

    half_range = 0.5 * max(x_max - x_min, y_max - y_min) * 1.1

    ax.set_xlim(x_center - half_range, x_center + half_range)
    ax.set_ylim(y_center - half_range, y_center + half_range)
    ax.set_aspect("equal", adjustable="box")

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.grid(False)

    plt.tight_layout()

    # ============================================================
    # 7) Save
    # ============================================================
    stem = "Fig4A_right_EVGTARY_cluster_medoid_mapping"
    out_svg = fig_dir / f"{stem}.svg"
    out_png = fig_dir / f"{stem}_600dpi.png"

    fig.savefig(out_svg, format="svg", bbox_inches="tight")
    fig.savefig(out_png, dpi=600, bbox_inches="tight")
    plt.close(fig)

    print(f"[SAVED] {out_svg}")
    print(f"[SAVED] {out_png}")


if __name__ == "__main__":
    main()