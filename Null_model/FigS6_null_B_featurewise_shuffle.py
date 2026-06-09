from __future__ import annotations

"""
Generate Fig. 1b null model B: feature-wise shuffle.

This script reproduces the bulk-organ UMAP embedding using the same preprocessing
and UMAP settings as the real-data panel, but independently shuffles each feature
column before PCA/UMAP.

Null model B = feature-wise shuffle.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
import umap.umap_ as umap


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

    csv_path = data_dir / "41organs_112525_with_system.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing input CSV: {csv_path}")

    print(f"[INFO] Input CSV: {csv_path}")

    # ============================================================
    # 2) Load table
    # ============================================================
    df_all = pd.read_csv(csv_path)
    df_all.columns = df_all.columns.astype(str).str.strip()

    # ============================================================
    # 3) Organ columns
    # ============================================================
    organ_map = {
        "B":  "Cerebrum",
        "C":  "Pituitary Gland",
        "D":  "Cerebellum",
        "E":  "Eye",
        "F":  "Tongue",
        "G":  "Salivary Gland",
        "H":  "Thyroid",
        "I":  "Lung",
        "J":  "Trachea",
        "K":  "Thymus",
        "L":  "Mammary Gland",
        "M":  "Internal Thoracic Artery",
        "N":  "Aorta",
        "O":  "Heart",
        "P":  "Liver",
        "Q":  "Gallbladder",
        "R":  "Spleen",
        "S":  "Pancreas",
        "T":  "Kidney",
        "U":  "Adrenal Gland",
        "V":  "Ureter",
        "W":  "Bladder",
        "X":  "Esophagus",
        "Y":  "Stomach",
        "Z":  "Small Intestine",
        "AA": "Colon",
        "AB": "Appendix",
        "AC": "Skin",
        "AD": "Skeletal Muscle",
        "AE": "Sciatic Nerve",
        "AF": "Spinal Cord",
        "AG": "Dorsal Root Ganglion",
        "AH": "Testis",
        "AI": "Prostate",
        "AJ": "Uterus",
        "AK": "Ovary",
        "AL": "Bone Marrow (Total)",
        "AM": "White Blood Cells",
        "AN": "Mononuclear Cells",
        "AO": "Plasma",
        "AP": "Serum",
    }

    organ_cols = [c for c in organ_map.keys() if c in df_all.columns]
    if not organ_cols:
        raise ValueError("No expected organ columns (B-AP) were found in the input CSV.")

    print(f"[INFO] Organ columns used: {len(organ_cols)}")

    # ============================================================
    # 4) Numeric preprocessing (same as real panel)
    # ============================================================
    df_num = (
        df_all[organ_cols]
        .apply(pd.to_numeric, errors="coerce")
        .fillna(0.0)
        .clip(lower=0.0)
    )
    x_counts = df_num.to_numpy(dtype=float)

    x_log = np.log1p(x_counts)
    row_sum = x_log.sum(axis=1, keepdims=True)
    mask_valid = row_sum[:, 0] > 0

    x_log = x_log[mask_valid]
    row_sum = row_sum[mask_valid]
    df_valid = df_all.loc[mask_valid].reset_index(drop=True)

    x_ratio = np.divide(
        x_log,
        row_sum,
        out=np.zeros_like(x_log),
        where=row_sum > 0,
    )
    x_ratio = np.nan_to_num(x_ratio, nan=0.0, posinf=0.0, neginf=0.0)

    col_std = x_ratio.std(axis=0)
    keep_mask = col_std > 0
    x_ratio = x_ratio[:, keep_mask]
    organ_cols_kept = [organ_cols[i] for i, k in enumerate(keep_mask) if k]

    print(f"[INFO] Non-zero-variance organ columns retained: {keep_mask.sum()} / {len(organ_cols)}")
    print(f"[INFO] Valid rows retained for embedding: {x_ratio.shape[0]}")

    if "system" not in df_valid.columns:
        raise ValueError("Input CSV must contain a precomputed 'system' column for null model B.")

    # ============================================================
    # 5) Null model B = feature-wise shuffle
    # ============================================================
    rng = np.random.default_rng(42)

    x_ratio_shuf = x_ratio.copy()
    for j in range(x_ratio_shuf.shape[1]):
        rng.shuffle(x_ratio_shuf[:, j])

    # ============================================================
    # 6) PCA -> UMAP (same settings as real panel)
    # ============================================================
    n_pca = min(10, x_ratio_shuf.shape[1])
    x_pca_shuf = PCA(
        n_components=n_pca,
        random_state=42,
        svd_solver="full",
    ).fit_transform(x_ratio_shuf)

    reducer_shuf = umap.UMAP(
        n_neighbors=30,
        min_dist=0.2,
        metric="cosine",
        random_state=42,
        low_memory=True,
        init="spectral",
    )
    embedding_shuf = reducer_shuf.fit_transform(x_pca_shuf)

    print(f"[INFO] Shuffled embedding shape: {embedding_shuf.shape}")

    # ============================================================
    # 7) Real system colors (labels preserved, structure broken)
    # ============================================================
    system_palette = {
        "Nervous":      "#3B4CC0",
        "Vascular":     "#4DBBD5",
        "Immune":       "#009A44",
        "Digestive":    "#E64B35",
        "Respiratory":  "#7E6148",
        "Skin/Musculo": "#F39B7F",
        "Urinary":      "#91D1C2",
        "Endocrine":    "#8491B4",
        "Exocrine":     "#DC0000",
        "Genital":      "#B09C85",
        "Sensory":      "#1F7A8C",
        "Blood":        "#C91066",
        "Other":        "#6E6E6E",
    }

    systems_real = df_valid["system"].astype(str).tolist()
    point_colors_real = [system_palette.get(s, "#BBBBBB") for s in systems_real]

    # ============================================================
    # 8) Save embedding CSV (recommended)
    # ============================================================
    out_csv = results_dir / "FigS6_bulk_null_B_featurewise_shuffle_embedding.csv"
    out_df = df_valid.copy()
    out_df["UMAP1"] = embedding_shuf[:, 0]
    out_df["UMAP2"] = embedding_shuf[:, 1]
    out_df.to_csv(out_csv, index=False)
    print(f"[SAVED] {out_csv}")

    # ============================================================
    # 9) Plot
    # ============================================================
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.scatter(
        embedding_shuf[:, 0],
        embedding_shuf[:, 1],
        c=point_colors_real,
        s=6,
        alpha=0.9,
        linewidths=0,
    )
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("UMAP1")
    ax.set_ylabel("UMAP2")
    ax.set_aspect("equal", adjustable="box")

    # publication-style: no title
    plt.tight_layout()

    # ============================================================
    # 10) Save figure
    # ============================================================
    stem = "FigS6_bulk_null_B_featurewise_shuffle"
    out_pdf = fig_dir / f"{stem}.pdf"
    out_png = fig_dir / f"{stem}_600dpi.png"

    fig.savefig(out_pdf, dpi=600)
    fig.savefig(out_png, dpi=600)
    plt.close(fig)

    print(f"[SAVED] {out_pdf}")
    print(f"[SAVED] {out_png}")


if __name__ == "__main__":
    main()