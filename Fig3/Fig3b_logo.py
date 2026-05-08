from __future__ import annotations

"""
Generate Fig. 3b Tier0 sequence logo panels.

This script reproduces the positive-only log-odds sequence logos shown in Fig. 3b
for the STLHQ and STFHQ motif-defined peptide sets in capillary and parenchymal layers.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import logomaker


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
    # 2) Load table
    # ============================================================
    df = pd.read_csv(csv_path)
    df["character"] = df["character"].astype(str)
    df["layer"] = df["layer"].astype(str).str.strip().str.lower()
    df["reads"] = pd.to_numeric(df["reads"], errors="coerce").fillna(0.0)

    required_cols = ["character", "layer", "reads"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    print(f"[INFO] Input rows: {len(df)}")

    # ============================================================
    # 3) Constants
    # ============================================================
    motifs = {
        "STLHQ": r"^STLHQ..$",
        "STFHQ": r"^STFHQ..$",
    }

    layers = ["capillary", "parenchyma"]

    aa = list("ACDEFGHIKLMNPQRSTVWY")
    aa2i = {a: i for i, a in enumerate(aa)}
    pseudocount = 0.5
    letter_color = "#2d2d2d"

    # ============================================================
    # 4) Helper functions
    # ============================================================
    def infer_length(series: pd.Series) -> int:
        lens = series.str.len().unique()
        if len(lens) != 1:
            raise ValueError(f"Non-constant motif length detected: {lens}")
        return int(lens[0])

    def build_bg_from_layer(allseq_df: pd.DataFrame, length: int) -> np.ndarray:
        """Read-weighted amino-acid background from all sequences within one layer."""
        counts = np.zeros(len(aa), dtype=float)
        for seq, weight in zip(allseq_df["character"].values, allseq_df["reads"].values):
            if len(seq) != length:
                continue
            for ch in seq:
                if ch in aa2i:
                    counts[aa2i[ch]] += weight
        counts += pseudocount
        return counts / counts.sum()

    def pos_counts_from_subset(sub_df: pd.DataFrame, length: int) -> np.ndarray:
        """Read-weighted position counts from unique peptides aggregated by sequence."""
        mat = np.zeros((length, len(aa)), dtype=float)
        agg = sub_df.groupby("character", as_index=False)["reads"].sum()
        for seq, weight in zip(agg["character"].values, agg["reads"].values):
            if len(seq) != length:
                continue
            for i, ch in enumerate(seq):
                if ch in aa2i:
                    mat[i, aa2i[ch]] += weight
        return mat

    def logodds_pssm(pos_counts: np.ndarray, bg: np.ndarray) -> np.ndarray:
        """PSSM as log2 odds relative to the layer-specific background."""
        pc = pos_counts + pseudocount
        p_pos = pc / pc.sum(axis=1, keepdims=True)
        return np.log2(np.clip(p_pos / bg[None, :], 1e-12, None))

    # ============================================================
    # 5) Pass 1: compute cache and shared global y-limit
    # ============================================================
    cache = {}
    ymax_list = []

    for motif_name, motif_regex in motifs.items():
        for layer in layers:
            layer_df = df[df["layer"] == layer].copy()
            if layer_df.empty:
                print(f"[WARN] No rows found for layer: {layer}")
                continue

            length = infer_length(layer_df["character"])
            bg = build_bg_from_layer(layer_df, length)

            tier0 = layer_df[layer_df["character"].str.fullmatch(motif_regex, na=False)].copy()
            print(
                f"[INFO] {motif_name} / {layer} | "
                f"Tier0 unique peptides: {tier0['character'].nunique()} | "
                f"total reads: {tier0['reads'].sum()}"
            )

            pos_counts = pos_counts_from_subset(tier0, length)
            pssm = logodds_pssm(pos_counts, bg)
            pssm_full = pd.DataFrame(pssm, columns=aa)

            pssm_pos = pssm_full.copy()
            pssm_pos[pssm_pos < 0] = 0.0

            cache[(motif_name, layer)] = {
                "pssm_pos": pssm_pos,
                "length": length,
            }
            ymax_list.append(float(pssm_pos.to_numpy().max()))

    if not ymax_list:
        raise ValueError("No motif/layer panels were generated. Check motif definitions and layer labels.")

    global_ymax = max(ymax_list) * 1.05
    print(f"[INFO] Global y-axis maximum: {global_ymax:.3f}")

    # ============================================================
    # 6) Pass 2: draw and save
    # ============================================================
    for motif_name in motifs.keys():
        for layer in layers:
            key = (motif_name, layer)
            if key not in cache:
                continue

            pssm_pos = cache[key]["pssm_pos"]
            length = cache[key]["length"]

            stem = f"Fig3B_Tier0_{motif_name}_{layer}_logo_posonly_fixedscale"
            out_svg = fig_dir / f"{stem}.svg"
            out_png = fig_dir / f"{stem}_600dpi.png"

            fig, ax = plt.subplots(figsize=(6, 2.2), dpi=300)

            logomaker.Logo(
                pssm_pos,
                ax=ax,
                color_scheme={a: letter_color for a in aa},
            )

            ax.set_ylabel("log2-odds", fontsize=11)
            ax.set_xticks(range(length))
            ax.set_xticklabels(range(1, length + 1))
            ax.set_ylim(0, global_ymax)

            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            plt.tight_layout()
            fig.savefig(out_svg, format="svg", bbox_inches="tight")
            fig.savefig(out_png, dpi=600, bbox_inches="tight")
            plt.close(fig)

            print(f"[SAVED] {out_svg}")
            print(f"[SAVED] {out_png}")


if __name__ == "__main__":
    main()