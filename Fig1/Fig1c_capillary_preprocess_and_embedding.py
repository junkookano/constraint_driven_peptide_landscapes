from __future__ import annotations

"""
Generate the processed capillary UMAP input for Fig. 1c.

This script reproduces the upstream preprocessing and embedding-generation step
used for the capillary UMAP analysis:
1) align rows by peptide character,
2) merge pancreas-related column 37 into column 11,
3) apply log1p transformation and row normalization,
4) remove zero-variance columns,
5) perform PCA and UMAP,
6) save the processed embedding table and trained UMAP model.

Input files correspond to the processed tables used to generate the final figure panel.
"""

from pathlib import Path

import joblib
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
    models_dir = base_dir / "models"

    results_dir.mkdir(parents=True, exist_ok=True)
    models_dir.mkdir(parents=True, exist_ok=True)

    meta_csv = data_dir / "df_capillary_pancreas_fixed.csv"
    counts_csv = data_dir / "normal_capillary.csv"

    if not meta_csv.exists():
        raise FileNotFoundError(f"Missing metadata CSV: {meta_csv}")
    if not counts_csv.exists():
        raise FileNotFoundError(f"Missing counts CSV: {counts_csv}")

    print(f"[INFO] Metadata CSV: {meta_csv}")
    print(f"[INFO] Raw counts CSV: {counts_csv}")

    # ============================================================
    # 2) Load tables
    # ============================================================
    df_meta = pd.read_csv(meta_csv)
    counts_df = pd.read_csv(counts_csv)

    for df in (df_meta, counts_df):
        df.columns = df.columns.map(lambda x: str(x).strip())

    if "character" not in df_meta.columns:
        raise ValueError("Metadata CSV must contain a 'character' column.")
    if "character" not in counts_df.columns:
        raise ValueError("Counts CSV must contain a 'character' column.")

    print(f"[INFO] Metadata rows: {len(df_meta)}")
    print(f"[INFO] Raw counts rows: {len(counts_df)}")

    # ============================================================
    # 3) Align row set and order to metadata table
    # ============================================================
    order = {ch: i for i, ch in enumerate(df_meta["character"].astype(str))}
    sub = counts_df[counts_df["character"].astype(str).isin(order.keys())].copy()
    sub["__ord__"] = sub["character"].astype(str).map(order)
    sub = sub.sort_values("__ord__").drop(columns="__ord__")

    if len(sub) != len(df_meta):
        raise ValueError(
            "Character alignment failed: the matched counts table length does not "
            "match the metadata table length. Please check for duplicated or missing characters."
        )

    if not sub["character"].astype(str).reset_index(drop=True).equals(
        df_meta["character"].astype(str).reset_index(drop=True)
    ):
        raise ValueError("Character order mismatch remained after alignment.")

    print(f"[INFO] Matched rows after character alignment: {len(sub)}")

    # ============================================================
    # 4) Select organ columns and merge column 37 into column 11
    # ============================================================
    organ_cols = [c for c in sub.columns if c.isdigit()]
    print(f"[INFO] Numeric organ columns before pancreas merge: {len(organ_cols)}")

    if "37" in organ_cols:
        sub["11"] = (
            pd.to_numeric(sub.get("11", 0), errors="coerce").fillna(0.0)
            + pd.to_numeric(sub["37"], errors="coerce").fillna(0.0)
        )
        sub = sub.drop(columns=["37"])
        organ_cols = [c for c in sub.columns if c.isdigit()]
        print("[INFO] Merged column 37 into column 11 and removed column 37.")
    else:
        print("[WARN] Column 37 was not found; no pancreas-column merge was performed.")

    print(f"[INFO] Numeric organ columns after pancreas merge: {len(organ_cols)}")

    # ============================================================
    # 5) Preprocessing: log1p -> row normalization -> zero-variance removal
    # ============================================================
    x = (
        sub[organ_cols]
        .apply(pd.to_numeric, errors="coerce")
        .fillna(0.0)
        .to_numpy(dtype=float)
    )

    x_log = np.log1p(x)
    row_sums = x_log.sum(axis=1, keepdims=True)
    valid_mask = row_sums[:, 0] > 0

    x_log = x_log[valid_mask]
    row_sums = row_sums[valid_mask]

    x_ratio = np.divide(
        x_log,
        row_sums,
        out=np.zeros_like(x_log),
        where=row_sums > 0,
    )

    col_std = x_ratio.std(axis=0)
    keep_mask = col_std > 0
    x_ratio = x_ratio[:, keep_mask]

    organs_kept = [organ_cols[i] for i, keep in enumerate(keep_mask) if keep]

    print(f"[INFO] Valid rows retained after filtering: {x_ratio.shape[0]}")
    print(f"[INFO] Non-zero-variance organ columns retained: {len(organs_kept)} / {len(organ_cols)}")

    # ============================================================
    # 6) PCA -> UMAP (9/18 settings)
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
        n_components=2,
    )
    emb = reducer.fit_transform(x_pca)

    print(f"[INFO] PCA output shape: {x_pca.shape}")
    print(f"[INFO] UMAP embedding shape: {emb.shape}")

    # ============================================================
    # 7) Save outputs
    # ============================================================
    out_df = df_meta.loc[valid_mask].copy()
    out_df["UMAP1"] = emb[:, 0]
    out_df["UMAP2"] = emb[:, 1]

    out_csv = results_dir / "df_capillary_pancreasFixed_unsupUMAP_cosine.csv"
    out_npy = results_dir / "umap_capillary_pancreasFixed_unsup_cosine.npy"
    out_pkl = models_dir / "umap_capillary_pancreasFixed_unsup_cosine.pkl"

    out_df.to_csv(out_csv, index=False)
    np.save(out_npy, emb)
    joblib.dump(reducer, out_pkl)

    print(f"[SAVED] {out_csv}")
    print(f"[SAVED] {out_npy}")
    print(f"[SAVED] {out_pkl}")


if __name__ == "__main__":
    main()