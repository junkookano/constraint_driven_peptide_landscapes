from __future__ import annotations

"""
Quantify shared-core density and global spread for null model B.

This script compares the real bulk embedding with the feature-wise shuffle
null embedding by measuring:

1) shared-core density:
   fraction of points within the real-data core radius

2) global spread from center:
   median distance from the real-data center

The real-data center is defined by the median UMAP coordinates of the real embedding.
The core radius is defined as the q-quantile of distances in the real embedding
(default q = 0.10).
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def distances_from_center(df: pd.DataFrame, center: np.ndarray) -> np.ndarray:
    xy = df[["UMAP1", "UMAP2"]].to_numpy()
    return np.sqrt(((xy - center) ** 2).sum(axis=1))


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

    path_real = data_dir / "umap_41organs_cosine_mcs50_withOrgan_with_system.csv"
    path_null = data_dir / "umap_41organs_cosine_mcs50_nullB_feature_shuffle.csv"

    if not path_real.exists():
        raise FileNotFoundError(f"Missing real embedding CSV: {path_real}")
    if not path_null.exists():
        raise FileNotFoundError(f"Missing null embedding CSV: {path_null}")

    print(f"[INFO] Real CSV: {path_real}")
    print(f"[INFO] Null B CSV: {path_null}")

    # ============================================================
    # 2) Load tables
    # ============================================================
    df_real = pd.read_csv(path_real)
    df_null = pd.read_csv(path_null)

    for name, df in [("Real", df_real), ("Null B", df_null)]:
        missing = [c for c in ["UMAP1", "UMAP2"] if c not in df.columns]
        if missing:
            raise ValueError(f"{name} CSV is missing required columns: {missing}")

    print(f"[INFO] Real rows: {len(df_real)}")
    print(f"[INFO] Null B rows: {len(df_null)}")

    # ============================================================
    # 3) Define center from real embedding
    # ============================================================
    center_x = float(np.median(df_real["UMAP1"].values))
    center_y = float(np.median(df_real["UMAP2"].values))
    center = np.array([center_x, center_y])

    print(f"[INFO] Real center: ({center_x:.4f}, {center_y:.4f})")

    # ============================================================
    # 4) Distances from center
    # ============================================================
    r_real = distances_from_center(df_real, center)
    r_null = distances_from_center(df_null, center)

    # ============================================================
    # 5) Core radius and summary metrics
    # ============================================================
    q = 0.10
    r_core = float(np.quantile(r_real, q))

    f_real = float(np.mean(r_real <= r_core))
    f_null = float(np.mean(r_null <= r_core))

    med_real = float(np.median(r_real))
    med_null = float(np.median(r_null))

    print("=== Shared-core quantification (feature-wise shuffle null) ===")
    print(f"[INFO] Core quantile q = {q:.2f}")
    print(f"[INFO] Core radius (from Real): {r_core:.4f}")
    print(f"[INFO] Core-in fraction: Real = {f_real:.4f}, Null B = {f_null:.4f}")
    print(f"[INFO] Median distance from center: Real = {med_real:.4f}, Null B = {med_null:.4f}")

    # ============================================================
    # 6) Sensitivity check
    # ============================================================
    sens_rows = []
    for q_test in [0.05, 0.10, 0.15]:
        r_core_q = float(np.quantile(r_real, q_test))
        f_real_q = float(np.mean(r_real <= r_core_q))
        f_null_q = float(np.mean(r_null <= r_core_q))

        sens_rows.append(
            {
                "q": q_test,
                "r_core": r_core_q,
                "core_fraction_real": f_real_q,
                "core_fraction_nullB": f_null_q,
            }
        )
        print(
            f"[INFO] Sensitivity q={q_test:.2f}: "
            f"r_core={r_core_q:.4f}, "
            f"Real={f_real_q:.4f}, Null B={f_null_q:.4f}"
        )

    # ============================================================
    # 7) Save summary tables
    # ============================================================
    summary_df = pd.DataFrame(
        [
            {
                "center_x": center_x,
                "center_y": center_y,
                "core_quantile_q": q,
                "core_radius": r_core,
                "core_fraction_real": f_real,
                "core_fraction_nullB": f_null,
                "median_distance_real": med_real,
                "median_distance_nullB": med_null,
            }
        ]
    )

    sensitivity_df = pd.DataFrame(sens_rows)

    summary_csv = results_dir / "FigS6_nullB_core_spread_summary.csv"
    sensitivity_csv = results_dir / "FigS6_nullB_core_spread_sensitivity.csv"

    summary_df.to_csv(summary_csv, index=False)
    sensitivity_df.to_csv(sensitivity_csv, index=False)

    print(f"[SAVED] {summary_csv}")
    print(f"[SAVED] {sensitivity_csv}")

    # ============================================================
    # 8) Bar plot 1: Shared-core density
    # ============================================================
    labels = ["Real", "Null B"]
    x = np.arange(len(labels))

    fig1, ax1 = plt.subplots(figsize=(4.0, 3.6))
    ax1.bar(x, [f_real, f_null])
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels)
    ax1.set_ylabel("Core-in fraction")
    ax1.set_title("Shared-core density")
    plt.tight_layout()

    core_pdf = fig_dir / "FigS6_shared_core_density.pdf"
    core_png = fig_dir / "FigS6_shared_core_density_600dpi.png"

    fig1.savefig(core_pdf, dpi=600, bbox_inches="tight")
    fig1.savefig(core_png, dpi=600, bbox_inches="tight")
    plt.close(fig1)

    print(f"[SAVED] {core_pdf}")
    print(f"[SAVED] {core_png}")

    # ============================================================
    # 9) Bar plot 2: Global spread from center
    # ============================================================
    fig2, ax2 = plt.subplots(figsize=(4.0, 3.6))
    ax2.bar(x, [med_real, med_null])
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels)
    ax2.set_ylabel("Median distance from center")
    ax2.set_title("Global spread from center")
    plt.tight_layout()

    spread_pdf = fig_dir / "FigS6_global_spread_from_center.pdf"
    spread_png = fig_dir / "FigS6_global_spread_from_center_600dpi.png"

    fig2.savefig(spread_pdf, dpi=600, bbox_inches="tight")
    fig2.savefig(spread_png, dpi=600, bbox_inches="tight")
    plt.close(fig2)

    print(f"[SAVED] {spread_pdf}")
    print(f"[SAVED] {spread_png}")


if __name__ == "__main__":
    main()