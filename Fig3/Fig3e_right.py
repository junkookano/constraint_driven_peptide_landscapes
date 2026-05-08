from __future__ import annotations

"""
Generate Fig. 3e right panel: interface-organ convergence bar plot.

This script reproduces the right-side panel of Fig. 3e by plotting the
convergence score for predefined interface organs, calculated as the product of
STLHQ and STFHQ enrichment ratios.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def pick_one(cols: list[str], desc: str) -> str:
    if not cols:
        raise KeyError(
            f"Expected column not found for: {desc}. "
            f"Available columns: {cols}"
        )
    return cols[0]


def main() -> None:
    # ============================================================
    # 1) Paths
    # ============================================================
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data"
    fig_dir = base_dir / "figs"

    fig_dir.mkdir(parents=True, exist_ok=True)

    csv_path = data_dir / "small_CPM_summary_table.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing input file: {csv_path}")

    print(f"[INFO] Input CSV: {csv_path}")

    # ============================================================
    # 2) Load table
    # ============================================================
    df = pd.read_csv(csv_path)

    required_cols = ["motif_family", "organ_name", "enrichment_ratio"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise KeyError(f"Missing required columns: {missing}")

    print(f"[INFO] Input rows: {len(df)}")

    # ============================================================
    # 3) Pivot table
    # ============================================================
    df_wide = df.pivot_table(
        index="organ_name",
        columns="motif_family",
        values="enrichment_ratio",
    )

    df_wide.columns = [f"enrichment_ratio_{col}" for col in df_wide.columns]
    df_wide = df_wide.reset_index()

    er_stl = pick_one(
        [c for c in df_wide.columns if c.startswith("enrichment_ratio_") and "STLHQ" in c],
        "STLHQ enrichment_ratio column",
    )
    er_stf = pick_one(
        [c for c in df_wide.columns if c.startswith("enrichment_ratio_") and "STFHQ" in c],
        "STFHQ enrichment_ratio column",
    )

    print(f"[INFO] STLHQ enrichment column: {er_stl}")
    print(f"[INFO] STFHQ enrichment column: {er_stf}")

    # ============================================================
    # 4) Predefined interface organs
    # ============================================================
    interface_orgs = [
        "liver_bile_ductal_cells",
        "spleen_red_pulp",
        "appendix_mucosa_epithelial_cells",
        "anterior_pituitary_gland",
    ]

    sub = df_wide[df_wide["organ_name"].isin(interface_orgs)].copy()
    if sub.empty:
        raise ValueError("None of the predefined interface organs were found in the input table.")

    # ============================================================
    # 5) Convergence score
    # ============================================================
    sub["convergence_score"] = sub[er_stl] * sub[er_stf]
    sub = sub.sort_values("convergence_score", ascending=True)

    print(f"[INFO] Interface organs plotted: {len(sub)}")

    # ============================================================
    # 6) Plot
    # ============================================================
    fig, ax = plt.subplots(figsize=(5, 3.4))

    ax.barh(
        y=sub["organ_name"],
        width=sub["convergence_score"],
        color="#4C72B0",
    )

    ax.set_xlabel("Convergence score (ER_STLHQ × ER_STFHQ)", fontsize=10)
    ax.set_ylabel("")
    ax.tick_params(axis="y", labelsize=8)
    ax.tick_params(axis="x", labelsize=8)

    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    for spine in ["left", "bottom"]:
        ax.spines[spine].set_linewidth(0.8)
        ax.spines[spine].set_color("#2d2d2d")

    plt.tight_layout()

    # ============================================================
    # 7) Save outputs
    # ============================================================
    stem = "Fig3E_right_interface_organ_convergence"
    out_svg = fig_dir / f"{stem}.svg"
    out_png = fig_dir / f"{stem}_600dpi.png"

    fig.savefig(out_svg, format="svg", bbox_inches="tight")
    fig.savefig(out_png, dpi=600, bbox_inches="tight")
    plt.close(fig)

    print(f"[SAVED] {out_svg}")
    print(f"[SAVED] {out_png}")


if __name__ == "__main__":
    main()