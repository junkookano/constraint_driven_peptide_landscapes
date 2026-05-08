from __future__ import annotations

"""
Generate Fig. 3f bootstrap bar-plot panels.

This script reproduces the bootstrap summary bar plots for the STLHQ and STFHQ
motif-defined peptide sets shown in Fig. 3f.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def prep(df: pd.DataFrame, layer_name: str) -> pd.DataFrame:
    df = df.copy()
    df["layer"] = layer_name

    err_lo = df["logodds_mean"] - df["logodds_ci025"]
    err_hi = df["logodds_ci975"] - df["logodds_mean"]

    bad = df[(err_lo < 0) | (err_hi < 0)]
    if not bad.empty:
        print(
            f"[INFO] {layer_name}: found {len(bad)} rows with near-zero floating-point "
            "CI asymmetry; negative errors were clipped to 0."
        )

    df["err_lo"] = err_lo.clip(lower=0)
    df["err_hi"] = err_hi.clip(lower=0)
    return df


def main() -> None:
    # ============================================================
    # 1) Paths
    # ============================================================
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data"
    fig_dir = base_dir / "figs"

    fig_dir.mkdir(parents=True, exist_ok=True)

    color_cap = "#4C72B0"
    color_par = "#E64B35"
    positions = [6, 7]

    families = {
        "STLHQ": {
            "cap_csv": data_dir / "capillary__pooled_all_organs__STLHQ_family__pssm_bootstrap_summary.csv",
            "par_csv": data_dir / "parenchyma__pooled_all_organs__STLHQ_family__pssm_bootstrap_summary.csv",
            "stem": "Fig3F_STLHQ_pos6-7_logodds_bootstrap_CI",
        },
        "STFHQ": {
            "cap_csv": data_dir / "capillary__pooled_all_organs__STFHQ_family__pssm_bootstrap_summary.csv",
            "par_csv": data_dir / "parenchyma__pooled_all_organs__STFHQ_family__pssm_bootstrap_summary.csv",
            "stem": "Fig3F_STFHQ_pos6-7_logodds_bootstrap_CI",
        },
    }

    for motif_name, cfg in families.items():
        cap_csv = cfg["cap_csv"]
        par_csv = cfg["par_csv"]

        for p in [cap_csv, par_csv]:
            if not p.exists():
                raise FileNotFoundError(f"Missing input file: {p}")

        print(f"[INFO] {motif_name} capillary CSV: {cap_csv}")
        print(f"[INFO] {motif_name} parenchyma CSV: {par_csv}")

        # ========================================================
        # 2) Load
        # ========================================================
        cap = pd.read_csv(cap_csv)
        par = pd.read_csv(par_csv)

        required_cols = ["position_1based", "logodds_mean", "logodds_ci025", "logodds_ci975"]
        for name, df in [("capillary", cap), ("parenchyma", par)]:
            missing = [c for c in required_cols if c not in df.columns]
            if missing:
                raise ValueError(f"{motif_name} {name} CSV missing columns: {missing}")

        cap = prep(cap, "capillary")
        par = prep(par, "parenchyma")
        all_df = pd.concat([cap, par], ignore_index=True)

        # ========================================================
        # 3) Pick the maximum log-odds AA for each layer x position
        # ========================================================
        pick = (
            all_df[all_df["position_1based"].isin(positions)]
            .sort_values(
                ["layer", "position_1based", "logodds_mean"],
                ascending=[True, True, False],
            )
            .groupby(["layer", "position_1based"], as_index=False)
            .head(1)
        )

        expected = len(positions) * 2
        if len(pick) != expected:
            raise ValueError(
                f"{motif_name}: expected {expected} rows "
                f"(2 layers × {len(positions)} positions), got {len(pick)}."
            )

        cap_pick = (
            pick[pick["layer"] == "capillary"]
            .set_index("position_1based")
            .loc[positions]
        )
        par_pick = (
            pick[pick["layer"] == "parenchyma"]
            .set_index("position_1based")
            .loc[positions]
        )

        # ========================================================
        # 4) Plot
        # ========================================================
        pos_labels = [f"pos{p}" for p in positions]
        y = list(range(len(positions)))
        bar_w = 0.35

        fig, ax = plt.subplots(figsize=(4.2, 3.2), dpi=300)

        ax.barh(
            [yi - bar_w / 2 for yi in y],
            cap_pick["logodds_mean"].values,
            height=bar_w,
            xerr=[cap_pick["err_lo"].values, cap_pick["err_hi"].values],
            color=color_cap,
            capsize=3,
            label="Capillary",
        )

        ax.barh(
            [yi + bar_w / 2 for yi in y],
            par_pick["logodds_mean"].values,
            height=bar_w,
            xerr=[par_pick["err_lo"].values, par_pick["err_hi"].values],
            color=color_par,
            capsize=3,
            label="Parenchyma",
        )

        ax.set_yticks(y)
        ax.set_yticklabels(pos_labels)
        ax.set_xlabel("Log-odds (bootstrap mean ± 95% CI)")
        ax.axvline(0, color="black", lw=0.8)

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.legend(frameon=False, fontsize=8, loc="best")

        plt.tight_layout()

        # ========================================================
        # 5) Save
        # ========================================================
        out_svg = fig_dir / f"{cfg['stem']}.svg"
        out_png = fig_dir / f"{cfg['stem']}_600dpi.png"

        fig.savefig(out_svg, format="svg", bbox_inches="tight")
        fig.savefig(out_png, dpi=600, bbox_inches="tight")
        plt.close(fig)

        print(f"[SAVED] {out_svg}")
        print(f"[SAVED] {out_png}")


if __name__ == "__main__":
    main()