from __future__ import annotations

"""
Generate Fig. 2b digital subtraction heatmap.

This script reproduces the visualization shown in Fig. 2b from the processed
bulk R1/R3 digital subtraction table.
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
    results_dir = base_dir / "results"

    fig_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    csv_path = data_dir / "bulk_R1R3_enrichment_Fig2_input_top3000.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing input file: {csv_path}")

    print(f"[INFO] Input CSV: {csv_path}")

    # ============================================================
    # 2) Load table
    # ============================================================
    df = pd.read_csv(csv_path)
    print(f"[INFO] Input rows: {len(df)}")

    required_cols = [
        "character",
        "subtraction_score",
        "E_cerebrum",
        "E_liver",
        "E_skeletal_muscle",
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # ============================================================
    # 3) Select top 50 positive subtraction-score peptides
    # ============================================================
    df_pos = df[df["subtraction_score"] > 0].copy()
    df_pos_sorted = df_pos.sort_values("subtraction_score", ascending=False)
    df_top50 = df_pos_sorted.head(50).copy()

    print(f"[INFO] Positive-score rows: {len(df_pos)}")
    print(f"[INFO] Top peptides retained for heatmap: {len(df_top50)}")

    df_top50_heatmap = df_top50[
        ["character", "subtraction_score", "E_cerebrum", "E_liver", "E_skeletal_muscle"]
    ].copy()

    # rank 1 at top of the heatmap
    df_plot = (
        df_top50_heatmap
        .rename(columns={"E_cortex": "E_cerebrum"})
        .sort_values("subtraction_score", ascending=True)
        .reset_index(drop=True)
    )

    assert df_plot.shape[0] == 50, f"Expected 50 rows, got {df_plot.shape[0]}"

    heat_values = df_plot[["E_cerebrum", "E_liver", "E_skeletal_muscle"]].to_numpy()

    # ============================================================
    # 4) Plot
    # ============================================================
    fig, ax = plt.subplots(
        figsize=(4.2, max(8, 0.22 * len(df_plot))),
        constrained_layout=True,
    )

    im = ax.imshow(
        heat_values,
        aspect="auto",
        cmap="YlGnBu",
        vmin=6,
        vmax=9,
    )

    ax.set_xticks(range(3))
    ax.set_xticklabels(
        ["Cerebrum", "Liver", "Skeletal muscle"],
        fontsize=9,
    )

    ax.set_yticks(range(len(df_plot)))
    ax.set_yticklabels(df_plot["character"], fontsize=6)
    ax.invert_yaxis()

    ax.set_xlabel("Organ (log2 enrichment)")
    ax.set_ylabel("Peptide (7-mer)")

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.02)
    cbar.set_label("log2 enrichment (R3 / R1)")

    # ============================================================
    # 5) Save outputs
    # ============================================================
    stem = "Fig2B_digital_subtraction_heatmap_top50"
    out_svg = fig_dir / f"{stem}.svg"
    out_png = fig_dir / f"{stem}_600dpi.png"

    fig.savefig(out_svg, format="svg", bbox_inches="tight")
    fig.savefig(out_png, dpi=600, bbox_inches="tight")
    plt.close(fig)

    print(f"[SAVED] {out_svg}")
    print(f"[SAVED] {out_png}")


if __name__ == "__main__":
    main()