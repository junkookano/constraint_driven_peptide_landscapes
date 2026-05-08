from __future__ import annotations

"""
Render the final Fig. 1c capillary UMAP panel (square, publication-style).

This version is intended for use as the manuscript panel:
- square plotting area
- no title
- no grid
- no legend
- fixed UMAP coordinates from the processed capillary table
- pancreas-fixed organ labels
- colors from color_of.json when available
"""

from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def canon_label(x) -> str:
    """Normalize labels such as 1, 1.0, '1' -> '1'."""
    if pd.isna(x):
        return "NA"
    s = str(x).strip()
    try:
        return str(int(float(s)))
    except Exception:
        return s


def sort_key(x: str):
    """Sort numeric labels numerically, otherwise by (length, string)."""
    try:
        return (0, int(float(x)))
    except Exception:
        return (1, len(x), x)


def main() -> None:
    # ============================================================
    # 1) Paths
    # ============================================================
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data"
    fig_dir = base_dir / "figs"

    fig_dir.mkdir(parents=True, exist_ok=True)

    csv_path = data_dir / "df_capillary_pancreasFixed_withOrganName.csv"
    color_json = data_dir / "color_of.json"

    if not csv_path.exists():
        raise FileNotFoundError(f"Missing input CSV: {csv_path}")

    print(f"[INFO] Input CSV: {csv_path}")
    print(f"[INFO] Color JSON: {color_json} (optional)")

    # ============================================================
    # 2) Load data
    # ============================================================
    df = pd.read_csv(csv_path)
    df.columns = df.columns.map(lambda x: str(x).strip())

    required_cols = ["UMAP1", "UMAP2"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    if "organ_label_pancreas_fixed" in df.columns:
        label_col = "organ_label_pancreas_fixed"
    elif "organ_label" in df.columns:
        label_col = "organ_label"
    else:
        raise ValueError(
            "Input CSV must contain either 'organ_label_pancreas_fixed' or 'organ_label'."
        )

    emb = df[["UMAP1", "UMAP2"]].to_numpy()
    labels = df[label_col].map(canon_label).to_numpy()

    print(f"[INFO] Label column used: {label_col}")
    print(f"[INFO] Number of points: {emb.shape[0]}")

    # ============================================================
    # 3) Load color map
    # ============================================================
    organ_to_color = {}
    if color_json.exists():
        with color_json.open("r") as f:
            raw = json.load(f)
        for k, v in raw.items():
            organ_to_color[str(k)] = tuple(v) if isinstance(v, (list, tuple)) else v
        print(f"[INFO] Loaded custom colors from: {color_json}")
    else:
        print("[WARN] color_of.json not found; using fallback palette only.")

    uniq = sorted(pd.unique(labels), key=sort_key)

    fallback_palette = (
        list(plt.cm.Set1.colors)
        + list(plt.cm.Set2.colors)
        + list(plt.cm.Set3.colors)
        + list(plt.cm.Dark2.colors)
        + list(plt.cm.Accent.colors)
        + list(plt.cm.Paired.colors)
        + list(plt.cm.tab20.colors)
        + list(plt.cm.tab20b.colors)
        + list(plt.cm.tab20c.colors)
        + list(plt.cm.Pastel1.colors)
        + list(plt.cm.Pastel2.colors)
    )

    if len(fallback_palette) < len(uniq):
        raise ValueError("Fallback palette does not contain enough colors.")

    fallback_map = {lab: fallback_palette[i] for i, lab in enumerate(uniq)}

    def color_for(lab: str):
        return organ_to_color.get(lab, fallback_map.get(lab, (0.6, 0.6, 0.6)))

    print("[INFO] First 20 labels:", labels[:20].tolist())
    print("[INFO] Labels missing from color_of.json:", sorted(set(labels) - set(organ_to_color.keys())))

    # ============================================================
    # 4) Plot (publication-style panel)
    # ============================================================
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_aspect("equal", adjustable="box")

    for u in uniq:
        mask = labels == u
        if not np.any(mask):
            continue

        color = color_for(u)

        ax.scatter(
            emb[mask, 0],
            emb[mask, 1],
            c=[color],
            s=8,
            alpha=0.88,
            edgecolors="k",
            linewidths=0.25,
        )

    # publication-style: no title, no grid, no ticks
    ax.set_xlabel("UMAP1")
    ax.set_ylabel("UMAP2")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)

    plt.tight_layout()

    # ============================================================
    # 5) Save outputs
    # ============================================================
    out_png = fig_dir / "Fig1c_capillary_panel_square.png"
    out_pdf = fig_dir / "Fig1c_capillary_panel_square.pdf"

    fig.savefig(out_png, dpi=600, bbox_inches="tight")
    fig.savefig(out_pdf, dpi=600, bbox_inches="tight")
    plt.close(fig)

    print(f"[SAVED] {out_png}")
    print(f"[SAVED] {out_pdf}")


if __name__ == "__main__":
    main()