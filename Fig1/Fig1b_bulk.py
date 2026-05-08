from __future__ import annotations

"""
Generate Fig. 1b bulk UMAP embedding.

This script reproduces the bulk-organ UMAP visualization shown in Fig. 1b.
Input CSV filenames are provisional and may be updated at final submission.
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
    results_dir = base_dir / "results"
    fig_dir = base_dir / "figs"

    fig_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    csv_path = data_dir / "41organs_112525.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing input file: {csv_path}")

    print(f"[INFO] Input CSV: {csv_path}")

    # ============================================================
    # 2) Load input table
    # ============================================================
    df_all = pd.read_csv(csv_path)
    df_all.columns = df_all.columns.astype(str).str.strip()

    # ============================================================
    # 3) Organ-column definition and organ-name mapping
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

    missing_cols = [c for c in organ_map.keys() if c not in df_all.columns]
    print(
        f"[INFO] Organ columns used: {len(organ_cols)} / {len(organ_map)} "
        f"(missing: {len(missing_cols)})"
    )

    df_num = (
        df_all[organ_cols]
        .apply(pd.to_numeric, errors="coerce")
        .fillna(0.0)
        .clip(lower=0.0)
    )
    x_counts = df_num.to_numpy(dtype=float)

    # ============================================================
    # 4) Dominant-organ assignment
    # ============================================================
    dom_idx = np.argmax(x_counts, axis=1)
    dom_letters = [organ_cols[i] for i in dom_idx]
    dom_organs = [organ_map[letter] for letter in dom_letters]

    df_all["organ_letter"] = dom_letters
    df_all["organ_name"] = dom_organs

    row_max = x_counts.max(axis=1, keepdims=True)
    n_ties = (x_counts == row_max).sum(axis=1)
    tie_n = int((n_ties > 1).sum())
    if tie_n > 0:
        print(f"[WARN] Dominant-organ ties detected in {tie_n} rows; argmax selects the first.")

    # ============================================================
    # 5) Organ-to-system mapping
    # ============================================================
    organ_to_system = {
        # Nervous
        "Cerebrum": "Nervous",
        "Pituitary Gland": "Nervous",
        "Cerebellum": "Nervous",
        "Sciatic Nerve": "Nervous",
        "Spinal Cord": "Nervous",
        "Dorsal Root Ganglion": "Nervous",

        # Vascular
        "Heart": "Vascular",
        "Internal Thoracic Artery": "Vascular",
        "Aorta": "Vascular",

        # Immune
        "Spleen": "Immune",
        "Thymus": "Immune",
        "Appendix": "Immune",

        # Blood
        "Bone Marrow (Total)": "Blood",
        "White Blood Cells": "Blood",
        "Mononuclear Cells": "Blood",
        "Plasma": "Blood",
        "Serum": "Blood",

        # Digestive
        "Liver": "Digestive",
        "Gallbladder": "Digestive",
        "Pancreas": "Digestive",
        "Esophagus": "Digestive",
        "Stomach": "Digestive",
        "Small Intestine": "Digestive",
        "Colon": "Digestive",

        # Respiratory
        "Lung": "Respiratory",
        "Trachea": "Respiratory",

        # Skin / Musculo
        "Skin": "Skin/Musculo",
        "Skeletal Muscle": "Skin/Musculo",

        # Urinary
        "Kidney": "Urinary",
        "Ureter": "Urinary",
        "Bladder": "Urinary",

        # Endocrine
        "Thyroid": "Endocrine",
        "Adrenal Gland": "Endocrine",

        # Exocrine
        "Salivary Gland": "Exocrine",
        "Mammary Gland": "Exocrine",

        # Genital
        "Testis": "Genital",
        "Prostate": "Genital",
        "Uterus": "Genital",
        "Ovary": "Genital",

        # Sensory
        "Eye": "Sensory",
        "Tongue": "Sensory",
    }

    df_all["system"] = df_all["organ_name"].map(organ_to_system)

    if df_all["system"].isna().any():
        missing = sorted(df_all.loc[df_all["system"].isna(), "organ_name"].unique())
        raise ValueError(f"Unmapped organ_name -> system detected: {missing}")

    # ============================================================
    # 6) Embedding pipeline: log1p -> row normalization -> PCA -> UMAP
    # ============================================================
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
    embedding = reducer.fit_transform(x_pca)
    print(f"[INFO] Embedding shape: {embedding.shape}")

    # ============================================================
    # 7) Plotting
    # ============================================================
    system_palette = {
        "Nervous": "#3B4CC0",
        "Vascular": "#4DBBD5",
        "Immune": "#009A44",
        "Digestive": "#E64B35",
        "Respiratory": "#7E6148",
        "Skin/Musculo": "#F39B7F",
        "Urinary": "#91D1C2",
        "Endocrine": "#8491B4",
        "Exocrine": "#DC0000",
        "Genital": "#B09C85",
        "Sensory": "#1F7A8C",
        "Blood": "#C91066",
    }

    unknown = set(df_valid["system"]) - set(system_palette.keys())
    if unknown:
        raise ValueError(f"Unknown system labels found: {unknown}")

    point_colors = [system_palette[s] for s in df_valid["system"]]

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.scatter(
        embedding[:, 0],
        embedding[:, 1],
        c=point_colors,
        s=6,
        alpha=0.9,
        linewidths=0,
    )
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("UMAP1")
    ax.set_ylabel("UMAP2")
    ax.set_title("Bulk organ constellation (system-colored)")

    stem = "Fig1b_bulk_UMAP_system"
    out_svg = fig_dir / f"{stem}.svg"
    out_png = fig_dir / f"{stem}_600dpi.png"

    fig.savefig(out_svg, format="svg", bbox_inches="tight")
    fig.savefig(out_png, dpi=600, bbox_inches="tight")
    plt.close(fig)

    print(f"[SAVED] {out_svg}")
    print(f"[SAVED] {out_png}")


if __name__ == "__main__":
    main()