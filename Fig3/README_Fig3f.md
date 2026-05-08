# README_Fig3f

## Purpose
This script reproduces **Fig. 3f** of the manuscript, which shows bootstrap-based log-odds summary bar plots for the STLHQ and STFHQ motif-defined peptide sets.

## Script
`Fig3f_bootstrap_barplots.py`

## Overview
The script performs the following steps:

1. Loads bootstrap summary tables for the STLHQ and STFHQ motif-defined peptide sets.
2. Reads capillary and parenchymal bootstrap summaries separately.
3. Computes lower and upper error-bar extents from the reported mean and 95% confidence interval bounds.
4. Selects positions 6 and 7.
5. For each layer and position, retains the amino acid with the highest bootstrap mean log-odds value.
6. Draws horizontal bar plots showing:
   - bootstrap mean log-odds
   - 95% confidence interval
   - capillary vs parenchyma comparison
7. Saves one panel for STLHQ and one panel for STFHQ.

---

## Input files
Place the following files in the `data/` directory located in the same folder as the script.

### STLHQ inputs
- `data/capillary__pooled_all_organs__STLHQ_family__pssm_bootstrap_summary.csv`
- `data/parenchyma__pooled_all_organs__STLHQ_family__pssm_bootstrap_summary.csv`

### STFHQ inputs
- `data/capillary__pooled_all_organs__STFHQ_family__pssm_bootstrap_summary.csv`
- `data/parenchyma__pooled_all_organs__STFHQ_family__pssm_bootstrap_summary.csv`

**Note:** The input filename corresponds to the processed table used for the final figure generation.
---

## Output files
Running the script generates the following files in the `figs/` directory:

- `figs/Fig3F_STLHQ_pos6-7_logodds_bootstrap_CI.svg`
- `figs/Fig3F_STLHQ_pos6-7_logodds_bootstrap_CI_600dpi.png`
- `figs/Fig3F_STFHQ_pos6-7_logodds_bootstrap_CI.svg`
- `figs/Fig3F_STFHQ_pos6-7_logodds_bootstrap_CI_600dpi.png`

The script creates the `figs/` directory automatically if it does not already exist.

---

## Required Python packages
The script requires the following Python packages:

- `pandas`
- `matplotlib`

---

## Example run
From the directory containing `Fig3f_bootstrap_barplots.py`, run:

```bash
python3 Fig3f_bootstrap_barplots.py
```

##Processing details

##Input tables

Each bootstrap summary CSV is expected to contain at least the following columns:

* position_1based
* logodds_mean
* logodds_ci025
* logodds_ci975

The script processes capillary and parenchymal tables separately for each motif-defined peptide set.

##Historical file labels

The input file names retain the historical label family, but in this study these sets are interpreted as motif-defined peptide sets rather than peptide families.

Position selection

The plot is restricted to:

* position 6
* position 7

These positions correspond to the unconstrained motif positions highlighted in the manuscript.

##Selection rule

For each combination of:

* layer (capillary or parenchyma)
* position (6 or 7)

the script retains the row with the largest bootstrap mean log-odds value.

Thus, the plotted bars represent the highest-scoring amino acid at each selected position for each layer.

Error bars

The horizontal error bars are derived from:

* lower error = logodds_mean - logodds_ci025
* upper error = logodds_ci975 - logodds_mean

If extremely small floating-point asymmetries produce negative values during this subtraction, these are clipped to zero before plotting.

##Floating-point note

Some rows in the bootstrap summary tables may show near-zero discrepancies between the reported mean and confidence-interval bounds due to floating-point precision effects. In such cases, negative error-bar components arising at the level of numerical roundoff are clipped to zero for plotting.

##Figure elements

The script produces one horizontal bar-plot panel per motif-defined peptide set:

* STLHQ
* STFHQ

Each panel shows:

* capillary bars
* parenchymal bars
* bootstrap mean log-odds values
* 95% confidence intervals
* a vertical reference line at zero

⸻

##Notes

* The file names retain the historical label “family,” but in this study these sets are interpreted as motif-defined peptide sets rather than peptide families.
* This script reproduces the bootstrap summary panel only; it does not perform bootstrap resampling upstream.
* The input CSV files are assumed to be processed bootstrap summary tables generated earlier in the analysis workflow.


⸻

##Directory structure
Fig3/
├── Fig3f_bootstrap_barplots.py
├── README_Fig3f.md
├── data/
│   ├── capillary__pooled_all_organs__STLHQ_family__pssm_bootstrap_summary.csv
│   ├── parenchyma__pooled_all_organs__STLHQ_family__pssm_bootstrap_summary.csv
│   ├── capillary__pooled_all_organs__STFHQ_family__pssm_bootstrap_summary.csv
│   └── parenchyma__pooled_all_organs__STFHQ_family__pssm_bootstrap_summary.csv
└── figs/