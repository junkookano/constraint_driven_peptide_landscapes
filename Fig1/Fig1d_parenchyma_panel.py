from __future__ import annotations

"""
Generate the Fig. 1d parenchyma UMAP panel.

This script reproduces the parenchyma UMAP embedding shown in Fig. 1d from a
wide-format count table whose organ columns are named like 1a, 1b, 2a, etc.

Color encodes organ number.
Marker shape encodes subtype.
The publication-style output panel is saved without legends.
"""

from pathlib import Path
from collections import defaultdict
import json
import re

import joblib
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
    models_dir = base_dir / "models"

    fig_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)
    models_dir.mkdir(parents=True, exist_ok=True)

    in_csv = data_dir / "parenchyma.csv"
    color_json = data_dir / "color_of.json"

    if not in_csv.exists():
        raise FileNotFoundError(f"Missing input CSV: {in_csv}")

    print(f"[INFO] Input CSV: {in_csv}")
    print(f"[INFO] Color JSON: {color_json} (optional)")

    # ============================================================
    # 2) Load table and parse organ columns
    # ============================================================
    df = pd.read_csv(in_csv)
    df.columns = df.columns.map(lambda s: str(s).strip())

    if "character" not in df.columns:
        raise ValueError("Input CSV must contain a 'character' column.")

    pattern = re.compile(r"^(\d{1,3})([A-Za-z]+)?$")
    organ_cols: list[str] = []
    parsed: dict[str, tuple[int, str]] = {}

    for col in df.columns:
        if col == "character":
            continue
        match = pattern.match(col)
        if match:
            num = int(match.group(1))
            sub = (match.group(2) or "").lower()
            organ_cols.append(col)
            parsed[col] = (num, sub)

    if not organ_cols:
        raise ValueError(
            f"No organ columns were detected. First 10 columns: {df.columns[:10].tolist()}"
        )

    print(f"[INFO] Parsed organ columns: {len(organ_cols)}")

    # ============================================================
    # 3) Numeric preprocessing
    # ============================================================
    x = (
        df[organ_cols]
        .apply(pd.to_numeric, errors="coerce")
        .fillna(0.0)
        .to_numpy(dtype=float)
    )
    x[x < 0] = 0.0

    row_sum_raw = x.sum(axis=1)
    mask_keep = row_sum_raw > 0

    if mask_keep.sum() < len(df):
        print(f"[INFO] All-zero rows removed: {(~mask_keep).sum()} / {len(df)}")

    x = x[mask_keep]
    df_used = df.loc[mask_keep].reset_index(drop=True)

    x_log = np.log1p(x)
    row_sum = x_log.sum(axis=1, keepdims=True)
    x_ratio = np.divide(
        x_log,
        row_sum,
        out=np.zeros_like(x_log),
        where=row_sum > 0,
    )

    col_std = x_ratio.std(axis=0)
    keep_cols = col_std > 0
    x_ratio = x_ratio[:, keep_cols]

    organ_kept_cols = [c for c, keep in zip(organ_cols, keep_cols) if keep]
    parsed_kept = {c: parsed[c] for c in organ_kept_cols}

    print(f"[INFO] Non-zero-variance organ columns retained: {len(organ_kept_cols)} / {len(organ_cols)}")
    print(f"[INFO] Rows retained for embedding: {x_ratio.shape[0]}")

    # ============================================================
    # 4) PCA -> UMAP (9/18 setting, cosine)
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
    embedding = reducer.fit_transform(x_pca)

    print(f"[INFO] PCA output shape: {x_pca.shape}")
    print(f"[INFO] UMAP embedding shape: {embedding.shape}")

    # ============================================================
    # 5) Assign dominant organ number and subtype
    # ============================================================
    arr = df_used[organ_kept_cols].to_numpy(dtype=float)

    num_to_idx = defaultdict(list)
    for j, col in enumerate(organ_kept_cols):
        num, sub = parsed_kept[col]
        num_to_idx[num].append(j)

    nums_sorted = sorted(num_to_idx.keys())
    num_sum = np.stack([arr[:, num_to_idx[n]].sum(axis=1) for n in nums_sorted], axis=1)
    dom_num_idx = np.argmax(num_sum, axis=1)
    dom_num = np.array([nums_sorted[i] for i in dom_num_idx])

    row_argmax_col = np.argmax(arr, axis=1)
    dom_sub = np.array([parsed_kept[organ_kept_cols[j]][1] or "-" for j in row_argmax_col])

    # ============================================================
    # 6) Colors and markers
    # ============================================================
    num_to_color: dict[int, tuple | str] = {}

    if color_json.exists():
        try:
            raw = json.loads(color_json.read_text())
            for k, v in raw.items():
                num_to_color[int(k)] = tuple(v) if isinstance(v, (list, tuple)) else v
            print(f"[INFO] Loaded custom colors from: {color_json}")
        except Exception as e:
            print(f"[WARN] Failed to read color_of.json: {e}")

    fallback = (
        list(plt.cm.tab20.colors)
        + list(plt.cm.tab20b.colors)
        + list(plt.cm.tab20c.colors)
    )
    for i, n in enumerate(sorted(set(dom_num))):
        if n not in num_to_color:
            num_to_color[n] = fallback[i % len(fallback)]

    marker_cycle = ["o", "s", "^", "v", "D", "P", "X", "*", "<", ">", "p", "H", "8", "d"]
    subtypes = sorted(set(dom_sub))
    sub_to_marker = {s: marker_cycle[i % len(marker_cycle)] for i, s in enumerate(subtypes)}

    print(f"[INFO] Unique dominant organ numbers: {len(set(dom_num))}")
    print(f"[INFO] Unique subtypes: {sorted(set(dom_sub))}")

    # ============================================================
    # 7) Plot (publication-style panel)
    # ============================================================
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_aspect("equal", adjustable="box")

    for n in sorted(set(dom_num)):
        for s in sorted(set(dom_sub)):
            mask = (dom_num == n) & (dom_sub == s)
            if not np.any(mask):
                continue

            ax.scatter(
                embedding[mask, 0],
                embedding[mask, 1],
                c=[num_to_color[n]],
                s=10,
                alpha=0.85,
                marker=sub_to_marker[s],
                edgecolors="k",
                linewidths=0.25,
            )

    ax.set_xlabel("UMAP1")
    ax.set_ylabel("UMAP2")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)

    plt.tight_layout()

    # ============================================================
    # 8) Save outputs
    # ============================================================
    out_png = fig_dir / "Fig1d_parenchyma_panel_square.png"
    out_pdf = fig_dir / "Fig1d_parenchyma_panel_square.pdf"
    out_npy = results_dir / "parenchyma_umap_cosine.npy"
    out_pkl = models_dir / "parenchyma_umap_cosine.pkl"
    out_csv = results_dir / "parenchyma_umap_cosine.csv"

    fig.savefig(out_png, dpi=600, bbox_inches="tight")
    fig.savefig(out_pdf, dpi=600, bbox_inches="tight")
    plt.close(fig)

    np.save(out_npy, embedding)
    joblib.dump(reducer, out_pkl)

    pd.DataFrame(
        {
            "character": df_used["character"].astype(str).values,
            "UMAP1": embedding[:, 0],
            "UMAP2": embedding[:, 1],
            "organ_number": dom_num,
            "subtype": dom_sub,
        }
    ).to_csv(out_csv, index=False)

    print(f"[SAVED] {out_png}")
    print(f"[SAVED] {out_pdf}")
    print(f"[SAVED] {out_npy}")
    print(f"[SAVED] {out_pkl}")
    print(f"[SAVED] {out_csv}")


if __name__ == "__main__":
    main()