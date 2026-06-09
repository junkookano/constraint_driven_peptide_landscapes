from __future__ import annotations

"""
Generate Fig. S6 null model A: label-permuted coloring.

This script reproduces the bulk-organ UMAP embedding using the same preprocessing
and UMAP settings as the real-data panel, but permutes the system labels before
coloring the points.

Null model A = label-permuted coloring.
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

    fig_dir.mkdir(parents=True, exist_ok=True)

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
    # 4) Numeric preprocessing (same as Fig1b)
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

    print(f"[INFO] Non-zero-variance organ columns retained: {keep_mask.sum()} / {len(organ_cols)}")
    print(f"[INFO] Valid rows retained for embedding: {x_ratio.shape[0]}")

    # ============================================================
    # 5) PCA -> UMAP (same settings as Fig1b)
    # ============================================================
    n_pca = min(10, x_ratio.shape[1])
    x_pca = PCA(
        n_components=n_pca,
        random_state=42,
        svd_solver="full",
    ).fit_transform(x_ratio)

    reducer = umap.UMAP(
        n_neighbors=30,
        min_dist=0.2,
        metric="cosine",
        random_state=42,
        low_memory=True,
        init="spectral",
    )
    emb_real = reducer.fit_transform(x_pca)
    print(f"[INFO] Embedding shape: {emb_real.shape}")

    # ============================================================
    # 6) System labels and permutation
    # ============================================================
    if "system" not in df_valid.columns:
        raise ValueError("Input CSV must contain a precomputed 'system' column for null model A.")

    systems_real = df_valid["system"].astype(str).tolist()

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

    rng = np.random.default_rng(42)
    systems_shuffled = systems_real.copy()
    rng.shuffle(systems_shuffled)

    point_colors_shuf = [system_palette.get(s, "#BBBBBB") for s in systems_shuffled]

    # ============================================================
    # 7) Plot
    # ============================================================
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.scatter(
        emb_real[:, 0],
        emb_real[:, 1],
        c=point_colors_shuf,
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
    # 8) Save
    # ============================================================
    stem = "FigS6_bulk_null_A_label_permuted"
    out_pdf = fig_dir / f"{stem}.pdf"
    out_png = fig_dir / f"{stem}_600dpi.png"

    fig.savefig(out_pdf, dpi=600)
    fig.savefig(out_png, dpi=600)
    plt.close(fig)

    print(f"[SAVED] {out_pdf}")
    print(f"[SAVED] {out_png}")


if __name__ == "__main__":
    main()