from __future__ import annotations

"""
Generate Fig. 3e left panel: organ-resolved enrichment bar plots.

This script reproduces the organ-resolved enrichment panel for the STLHQ and STFHQ
motif-defined peptide sets from a processed summary table.
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

    fig_dir.mkdir(parents=True, exist_ok=True)

    csv_path = data_dir / "small_CPM_summary_table.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing input file: {csv_path}")

    print(f"[INFO] Input CSV: {csv_path}")

    # ============================================================
    # 2) Settings
    # ============================================================
    q_cutoff = 0.05
    topn_stl = 12
    save_basename = "Fig3E_left_organwise_enrichment"

    stl_key = "STLHQ_FAMILY"
    stf_key = "STFHQ_FAMILY"

   
    # ============================================================
    # 3) Load + cleanup
    # ============================================================
    df = pd.read_csv(csv_path)

    required_cols = ["motif_family", "organ_name", "enrichment_ratio", "qvalue"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df["motif_family"] = df["motif_family"].astype(str).str.strip()
    df["organ_name"] = df["organ_name"].astype(str).str.strip()
    df["enrichment_ratio"] = pd.to_numeric(df["enrichment_ratio"], errors="coerce")
    df["qvalue"] = pd.to_numeric(df["qvalue"], errors="coerce")

    # ============================================================
    # 4) Split motif-defined sets
    # ============================================================
    stl = df[df["motif_family"].str.upper() == stl_key].copy()
    stf = df[df["motif_family"].str.upper() == stf_key].copy()

    stl_sig = stl[stl["qvalue"] < q_cutoff].copy()
    stf_sig = stf[stf["qvalue"] < q_cutoff].copy()

    if stl_sig.empty:
        raise ValueError("No significant STLHQ rows after q-value filtering.")
    if stf_sig.empty:
        raise ValueError("No significant STFHQ rows after q-value filtering.")

    stl_main = stl_sig.sort_values("enrichment_ratio", ascending=False).head(topn_stl).copy()
    stf_main = stf_sig.sort_values("enrichment_ratio", ascending=False).copy()

    def clip_pos(x):
        return np.clip(x, 1e-12, None)

    stl_main["enr_plot"] = clip_pos(stl_main["enrichment_ratio"].values)
    stf_main["enr_plot"] = clip_pos(stf_main["enrichment_ratio"].values)

    stl_main = stl_main.sort_values("enr_plot", ascending=True)
    stf_main = stf_main.sort_values("enr_plot", ascending=True)

    print(f"[INFO] STLHQ significant rows: {len(stl_sig)}")
    print(f"[INFO] STFHQ significant rows: {len(stf_sig)}")
    print(f"[INFO] STLHQ rows plotted: {len(stl_main)}")
    print(f"[INFO] STFHQ rows plotted: {len(stf_main)}")

    # ============================================================
    # 5) Plot
    # ============================================================
    fig, axes = plt.subplots(
        nrows=1,
        ncols=2,
        figsize=(11, 6),
        constrained_layout=True,
    )

    # Left: STLHQ motif-defined set
    ax = axes[0]
    ax.barh(stl_main["organ_name"], stl_main["enr_plot"])
    ax.set_xscale("log")
    ax.set_xlabel("Enrichment ratio (log scale)")
    ax.set_ylabel("Organ")

    # Right: STFHQ motif-defined set
    ax = axes[1]
    ax.barh(stf_main["organ_name"], stf_main["enr_plot"])
    ax.set_xscale("log")
    ax.set_xlabel("Enrichment ratio (log scale)")
    ax.set_ylabel("")

    xmax = max(stl_main["enr_plot"].max(), stf_main["enr_plot"].max()) * 1.2
    xmin = min(stl_main["enr_plot"].min(), stf_main["enr_plot"].min()) / 1.2
    for ax in axes:
        ax.set_xlim(left=xmin, right=xmax)

    # ============================================================
    # 6) Save outputs
    # ============================================================
    out_svg = fig_dir / f"{save_basename}.svg"
    out_png = fig_dir / f"{save_basename}_600dpi.png"

    fig.savefig(out_svg, format="svg", bbox_inches="tight")
    fig.savefig(out_png, dpi=600, bbox_inches="tight")
    plt.close(fig)

    print(f"[SAVED] {out_svg}")
    print(f"[SAVED] {out_png}")


if __name__ == "__main__":
    main()