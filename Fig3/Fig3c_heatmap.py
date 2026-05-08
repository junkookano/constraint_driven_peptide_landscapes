from __future__ import annotations

"""
Generate Fig. 3c heatmap panels.

This script reproduces the organ-by-layer enrichment heatmaps shown in Fig. 3c
for the STLHQ and STFHQ motif-defined peptide sets.
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

    csv_path = data_dir / "merged_cap_par_CPM.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing input file: {csv_path}")

    print(f"[INFO] Input CSV: {csv_path}")

    # ============================================================
    # 2) Settings
    # ============================================================
    top_n = 15
    families = {
        "STLHQ": r"^STLHQ..$",
        "STFHQ": r"^STFHQ..$",
    }
    layers = ["capillary", "parenchyma"]

    # ============================================================
    # 3) Load table
    # ============================================================
    df = pd.read_csv(csv_path)
    df["layer"] = df["layer"].astype(str).str.strip().str.lower()
    df["character"] = df["character"].astype(str).str.strip()
    df["CPM"] = pd.to_numeric(df["CPM"], errors="coerce")

    required_cols = ["organ_name", "layer", "character", "CPM"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df.dropna(subset=required_cols)
    df = df[df["CPM"] >= 0]

    print(f"[INFO] Input rows after cleaning: {len(df)}")

    # ============================================================
    # 4) Helper functions
    # ============================================================
    def family_table(regex: str) -> pd.DataFrame:
        """Compute log1p-summed family CPM per organ x layer."""
        sub = df[df["character"].str.match(regex, na=False)].copy()
        if sub.empty:
            raise ValueError(f"No rows matched regex: {regex}")

        agg = (
            sub.groupby(["organ_name", "layer"], as_index=False)["CPM"]
            .sum()
        )
        agg["log1pCPM"] = np.log1p(agg["CPM"])

        pv = agg.pivot(index="organ_name", columns="layer", values="log1pCPM")

        for lay in layers:
            if lay not in pv.columns:
                pv[lay] = 0.0

        pv = pv[layers].fillna(0.0)
        pv["rank_score"] = pv.max(axis=1)
        pv = pv.sort_values("rank_score", ascending=False)

        return pv

    def plot_heatmap(pv: pd.DataFrame, family_name: str) -> None:
        """Plot one Top-N organ x layer heatmap."""
        top = pv.head(top_n).drop(columns=["rank_score"])
        mat = top.to_numpy()

        vals = mat[np.isfinite(mat)]
        vals_pos = vals[vals > 0]
        vmax = np.percentile(vals_pos, 95) if len(vals_pos) else 1.0

        fig, ax = plt.subplots(figsize=(4.4, 6.0), dpi=300)

        im = ax.imshow(
            mat,
            aspect="auto",
            cmap="YlGnBu",
            vmin=0,
            vmax=vmax,
        )

        ax.set_xticks([0, 1])
        ax.set_xticklabels(["Capillary", "Parenchyma"])
        ax.set_yticks(range(len(top.index)))
        ax.set_yticklabels(top.index, fontsize=8)
        ax.set_xlabel("Layer")
        ax.set_ylabel("Organ / microenvironment")

        cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.02)
        cbar.set_label("log1p(CPM)", rotation=90)

        plt.tight_layout()

        stem = f"Fig3C_Main_Top{top_n}_{family_name}_log1pCPM"
        out_svg = fig_dir / f"{stem}.svg"
        out_png = fig_dir / f"{stem}_600dpi.png"

        fig.savefig(out_svg, format="svg", bbox_inches="tight")
        fig.savefig(out_png, dpi=600, bbox_inches="tight")
        plt.close(fig)

        print(f"[SAVED] {out_svg}")
        print(f"[SAVED] {out_png}")

    # ============================================================
    # 5) Run
    # ============================================================
    for family_name, regex in families.items():
        pv = family_table(regex)
        print(f"[INFO] {family_name}: organs in table = {len(pv)}")
        plot_heatmap(pv, family_name)


if __name__ == "__main__":
    main()