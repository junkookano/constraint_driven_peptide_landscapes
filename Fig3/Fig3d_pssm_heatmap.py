from __future__ import annotations

"""
Generate Fig. 3d PSSM heatmap panels.

This script reproduces the PSSM heatmaps shown in Fig. 3d for the STLHQ and STFHQ
motif families using precomputed log-odds matrices.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


AA_ORDER = list("ACDEFGHIKLMNPQRSTVWY")


def load_posxAA_to_AAxpos(csv_path: Path) -> tuple[np.ndarray, list[str]]:
    """
    Load a PSSM CSV with:
      rows = positions (0..6 or 1..7)
      columns = amino acids (A,C,...,Y)

    Returns:
      mat: (20, 7) array with rows = amino acids, cols = positions 1..7
      pos_labels: ['1', '2', ..., '7']
    """
    df = pd.read_csv(csv_path, index_col=0)

    df.columns = [str(c).strip().upper() for c in df.columns]
    missing = [aa for aa in AA_ORDER if aa not in df.columns]
    if missing:
        raise ValueError(f"{csv_path.name} is missing AA columns: {missing}")

    df = df[AA_ORDER]

    try:
        pos_int = np.array([int(str(x)) for x in df.index])
    except Exception:
        raise ValueError(
            f"Position index in {csv_path.name} is not integer-like: {df.index[:10].tolist()}"
        )

    # Normalize 1..7 -> 0..6 if needed
    if pos_int.min() == 1:
        pos_int = pos_int - 1

    if not np.array_equal(np.sort(pos_int), np.arange(7)):
        raise ValueError(
            f"Unexpected position index in {csv_path.name}: {pos_int.tolist()}"
        )

    order = np.argsort(pos_int)
    df = df.iloc[order, :]
    pos_int = pos_int[order]

    mat = df.to_numpy().T  # shape (20, 7), AA x position
    pos_labels = [str(i) for i in range(1, 8)]

    return mat, pos_labels


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

    stl_path = data_dir / "STLHQ_family_PSSM_logodds.csv"
    stf_path = data_dir / "STFHQ_family_PSSM_logodds.csv"

    for p in [stl_path, stf_path]:
        if not p.exists():
            raise FileNotFoundError(f"Missing input file: {p}")

    print(f"[INFO] STLHQ PSSM input: {stl_path}")
    print(f"[INFO] STFHQ PSSM input: {stf_path}")

    # ============================================================
    # 2) Load matrices
    # ============================================================
    mat_stl, pos_labels = load_posxAA_to_AAxpos(stl_path)
    mat_stf, _ = load_posxAA_to_AAxpos(stf_path)
    aa_labels = AA_ORDER

    print(f"[INFO] STLHQ matrix shape: {mat_stl.shape}")
    print(f"[INFO] STFHQ matrix shape: {mat_stf.shape}")

    # ============================================================
    # 3) Shared color scale
    # ============================================================
    all_vals = np.concatenate([mat_stl.ravel(), mat_stf.ravel()])
    maxabs = float(np.percentile(np.abs(all_vals), 98))
    if maxabs == 0:
        maxabs = 1.0
    vmin, vmax = -maxabs, maxabs

    print(f"[INFO] Shared color scale: vmin={vmin:.3f}, vmax={vmax:.3f}")

    # ============================================================
    # 4) Plot
    # ============================================================
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 4.2), constrained_layout=True)

    cmap = "RdBu_r"

    im0 = axes[0].imshow(mat_stl, aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax)
    axes[0].set_xlabel("Position")
    axes[0].set_ylabel("Amino acid")
    axes[0].set_yticks(range(len(aa_labels)))
    axes[0].set_yticklabels(aa_labels)
    axes[0].set_xticks(range(len(pos_labels)))
    axes[0].set_xticklabels(pos_labels)

    im1 = axes[1].imshow(mat_stf, aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax)
    axes[1].set_xlabel("Position")
    axes[1].set_ylabel("")
    axes[1].set_yticks(range(len(aa_labels)))
    axes[1].set_yticklabels([])
    axes[1].set_xticks(range(len(pos_labels)))
    axes[1].set_xticklabels(pos_labels)

    cbar = fig.colorbar(im1, ax=axes, fraction=0.046, pad=0.02)
    cbar.set_label("log-odds score", rotation=90)

    for ax in axes:
        ax.tick_params(length=0)
        for spine in ax.spines.values():
            spine.set_visible(False)

    # ============================================================
    # 5) Save outputs
    # ============================================================
    stem = "Fig3D_PSSM_heatmap_STLHQ_STFHQ_sharedCB"
    svg_path = fig_dir / f"{stem}.svg"
    png_path = fig_dir / f"{stem}_600dpi.png"

    fig.savefig(svg_path, format="svg", bbox_inches="tight")
    fig.savefig(png_path, dpi=600, bbox_inches="tight")
    plt.close(fig)

    print(f"[SAVED] {svg_path}")
    print(f"[SAVED] {png_path}")


if __name__ == "__main__":
    main()