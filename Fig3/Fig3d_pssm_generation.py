from __future__ import annotations

"""
Generate PSSM matrices and sequence logos for Fig. 3d.

This script creates counts, frequency, and log-odds PSSM tables for the
STLHQ_family and STFHQ_family motif families from the motif-family subset table.

The background model for log-odds is a uniform 20-amino-acid background.
"""

from pathlib import Path

import logomaker
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


AA_ALPHABET = list("ACDEFGHIKLMNPQRSTVWY")


def build_counts_matrix(seqs: list[str], weights: list[float], alphabet: list[str]) -> pd.DataFrame:
    length = len(seqs[0])
    counts = pd.DataFrame(0.0, index=range(length), columns=alphabet)

    for seq, w in zip(seqs, weights):
        for i, aa in enumerate(seq):
            if aa in alphabet:
                counts.loc[i, aa] += w

    return counts


def main() -> None:
    # ============================================================
    # 1) Paths
    # ============================================================
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data"
    results_dir = base_dir / "results"
    fig_dir = base_dir / "figs"

    results_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    in_csv = data_dir / "phase2.6_motif_family_subset_reads20.csv"
    if not in_csv.exists():
        raise FileNotFoundError(f"Missing input file: {in_csv}")

    print(f"[INFO] Input CSV: {in_csv}")

    # ============================================================
    # 2) Load table
    # ============================================================
    df_all = pd.read_csv(in_csv)

    required_cols = ["character", "reads", "motif_family"]
    missing = [c for c in required_cols if c not in df_all.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df_all["character"] = df_all["character"].astype(str).str.upper().str.strip()
    df_all["reads"] = pd.to_numeric(df_all["reads"], errors="coerce").fillna(0.0)
    df_all["motif_family"] = df_all["motif_family"].astype(str).str.strip()

    print(f"[INFO] Input rows: {len(df_all)}")

    # ============================================================
    # 3) Families to process
    # ============================================================
    families = ["STLHQ_family", "STFHQ_family"]

    for family in families:
        df = df_all[df_all["motif_family"] == family].copy()

        if df.empty:
            raise ValueError(f"No rows found for family: {family}")

        print(f"[INFO] {family} rows: {len(df)}")

        seqs = df["character"].tolist()
        weights = df["reads"].tolist()

        lengths = sorted(set(len(s) for s in seqs))
        if len(lengths) != 1:
            raise ValueError(f"{family} contains mixed sequence lengths: {lengths}")

        counts = build_counts_matrix(seqs, weights, AA_ALPHABET)
        freq = counts.div(counts.sum(axis=1), axis=0)

        # uniform 20-AA background
        bg = 1 / len(AA_ALPHABET)
        log_odds = np.log2(freq / bg)
        log_odds = log_odds.replace([np.inf, -np.inf], 0.0)

        # ========================================================
        # 4) Save tables
        # ========================================================
        counts_csv = results_dir / f"{family}_PSSM_counts.csv"
        freq_csv = results_dir / f"{family}_PSSM_freq.csv"
        logodds_csv = results_dir / f"{family}_PSSM_logodds.csv"

        counts.to_csv(counts_csv)
        freq.to_csv(freq_csv)
        log_odds.to_csv(logodds_csv)

        print(f"[SAVED] {counts_csv}")
        print(f"[SAVED] {freq_csv}")
        print(f"[SAVED] {logodds_csv}")

       


if __name__ == "__main__":
    main()