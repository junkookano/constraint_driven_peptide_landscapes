from __future__ import annotations

"""
Compare capillary pancreas-related labels 11 and 37 and assign a pancreas-fixed label.

This script evaluates whether labels 11 and 37 should be merged or whether one should
be retained preferentially, using:
1) exact Jaccard overlap,
2) Hamming-distance-1 fuzzy overlap,
3) position-wise PWM correlation,
4) simple heuristic quality scoring.

It then writes a new column, 'organ_label_pancreas_fixed', to the output table.
"""

from math import log
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr


AA = "ACDEFGHIKLMNPQRSTVWY"


def is7(seq: str) -> bool:
    seq = str(seq).strip().upper()
    return len(seq) == 7 and all(ch in AA for ch in seq)


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def neighbors_h1(seq: str) -> set[str]:
    outs = {seq}
    for i, ch in enumerate(seq):
        for aa in AA:
            if aa != ch:
                outs.add(seq[:i] + aa + seq[i + 1 :])
    return outs


def fuzzy_shared_h1(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    bset = set(b)
    hit = 0
    for s in a:
        if neighbors_h1(s) & bset:
            hit += 1
    return hit / len(a)


def pwm(seqset: set[str]) -> np.ndarray:
    if not seqset:
        return np.zeros((7, 20))
    aa2i = {a: i for i, a in enumerate(AA)}
    mat = np.zeros((7, 20), dtype=float)
    for s in seqset:
        for i, ch in enumerate(s):
            mat[i, aa2i[ch]] += 1
    mat = (mat.T / (mat.sum(axis=1) + 1e-9)).T
    return mat


def pwm_mean_corr(p: np.ndarray, q: np.ndarray) -> float:
    rs = []
    for i in range(7):
        if p[i].std() > 0 and q[i].std() > 0:
            r, _ = pearsonr(p[i], q[i])
        else:
            r = 0.0
        rs.append(r)
    return float(np.mean(rs))


def entropy_of(df: pd.DataFrame, colname: str) -> float:
    if colname not in df.columns:
        return np.nan
    x = pd.to_numeric(df[colname], errors="coerce").fillna(0).values
    if x.sum() <= 0:
        return np.nan
    p = x / x.sum()
    p = p[p > 0]
    return float(-np.sum(p * np.log(p)))


def pick_set(df: pd.DataFrame, has_label: bool, lab: pd.Series | None, org_id: int) -> set[str]:
    if has_label and lab is not None:
        s = set(
            df.loc[(lab == org_id) & df["character"].apply(is7), "character"]
            .astype(str)
            .str.upper()
        )
        if len(s) > 0:
            return s

    col = str(org_id)
    if col in df.columns:
        s = set(
            df.loc[
                (pd.to_numeric(df[col], errors="coerce").fillna(0) > 0)
                & df["character"].apply(is7),
                "character",
            ]
            .astype(str)
            .str.upper()
        )
        return s

    return set()


def main() -> None:
    # ============================================================
    # 1) Paths
    # ============================================================
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data"
    results_dir = base_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    in_csv = data_dir / "df_normal_capillary_unsup_umap_hdbscan_cosine_mcs50.csv"
    out_csv = results_dir / "df_capillary_pancreas_fixed.csv"

    if not in_csv.exists():
        raise FileNotFoundError(f"Missing input CSV: {in_csv}")

    print(f"[INFO] Input CSV: {in_csv}")

    # ============================================================
    # 2) Load table
    # ============================================================
    df = pd.read_csv(in_csv)
    df.columns = df.columns.map(lambda x: str(x).strip())

    has_label = "organ_label" in df.columns
    if has_label:
        lab = pd.to_numeric(df["organ_label"], errors="coerce").astype("Int64")
    else:
        lab = None

    # ============================================================
    # 3) Compare label 11 vs 37
    # ============================================================
    s11 = pick_set(df, has_label, lab, 11)
    s37 = pick_set(df, has_label, lab, 37)

    print(f"#11 n={len(s11)} | #37 n={len(s37)}")

    small_min = 50
    too_small = []
    if len(s11) < small_min:
        too_small.append(11)
    if len(s37) < small_min:
        too_small.append(37)

    j = jaccard(s11, s37)
    f11in37 = fuzzy_shared_h1(s11, s37)
    f37in11 = fuzzy_shared_h1(s37, s11)

    print(
        f"Jaccard(exact)={j:.3f} | "
        f"fuzzy<=1: 11->37={f11in37:.3f}, 37->11={f37in11:.3f}"
    )

    p11 = pwm(s11)
    p37 = pwm(s37)
    r = pwm_mean_corr(p11, p37)
    print(f"PWM position-wise mean Pearson r = {r:.3f}")

    h11 = entropy_of(df, "11")
    h37 = entropy_of(df, "37")
    print(f"Entropy proxy: H(11)={h11:.3f}, H(37)={h37:.3f}")

    unify = (j >= 0.3) and (min(f11in37, f37in11) >= 0.6) and (r >= 0.8)

    if too_small and len(too_small) == 1:
        action = "pick11" if too_small[0] == 37 else "pick37"
        reason = f"one set too small (<{small_min})"
    elif unify:
        action = "merge"
        reason = "high similarity (exact + fuzzy + PWM)"
    else:
        score11 = (len(s11) > 0) + (1.0 if not np.isnan(h11) else 0.0) + (1.0 - (h11 if not np.isnan(h11) else 1.0))
        score37 = (len(s37) > 0) + (1.0 if not np.isnan(h37) else 0.0) + (1.0 - (h37 if not np.isnan(h37) else 1.0))
        action = "pick11" if score11 >= score37 else "pick37"
        reason = f"similarity not high; choose higher-quality set ({'11' if action == 'pick11' else '37'})"

    action_text = {
        "merge": "merge (11 + 37)",
        "pick11": "retain 11 and collapse 37 into 11",
        "pick37": "retain 37 and collapse 11 into 37",
    }[action]

    print(f"[DECISION] {action_text} | reason: {reason}")

    # ============================================================
    # 4) Write pancreas-fixed label
    # ============================================================
    df2 = df.copy()

    if has_label:
        organ_num = pd.to_numeric(df2["organ_label"], errors="coerce").astype("Int64")
    else:
        organ_cols = [c for c in df2.columns if c.isdigit()]
        if not organ_cols:
            raise ValueError("No organ_label column and no numeric organ columns were found.")
        organ_num = pd.Series(np.argmax(df2[organ_cols].to_numpy(), axis=1), index=df2.index)
        organ_num = organ_num.map(lambda i: int(organ_cols[i]))

    if action == "merge":
        organ_num = organ_num.replace({37: 11})
    elif action == "pick11":
        organ_num = organ_num.replace({37: 11})
    elif action == "pick37":
        organ_num = organ_num.replace({11: 37})

    df2["organ_label_pancreas_fixed"] = organ_num
    df2.to_csv(out_csv, index=False)

    print(f"[SAVED] {out_csv}")


if __name__ == "__main__":
    main()