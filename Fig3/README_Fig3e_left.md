# README_Fig3e_left

## Purpose
This script reproduces the **left-side enrichment panel of Fig. 3e** of the manuscript, which shows organ-resolved enrichment ratios for the STLHQ and STFHQ motif-defined peptide sets.


## Overview
The script performs the following steps:

1. Loads a processed summary table of organ-wise enrichment statistics.
2. Separates rows corresponding to the historical file labels:
   - `STLHQ_family`
   - `STFHQ_family`
3. Filters rows by statistical significance (`qvalue < 0.05`).
4. Ranks organs by enrichment ratio.
5. Plots:
   - the top 12 significant organs for the STLHQ motif-defined set
   - all significant organs for the STFHQ motif-defined set
6. Saves the two-panel enrichment figure.

---
## Script
`Fig3e_left_enrichment.py`

## Input file
Place the following file in the `data/` directory located in the same folder as the script:

- `data/small_CPM_summary_table.csv`

**Note:** The input filename corresponds to the processed table used for the final figure generation.

---

## Output files
Running the script generates the following files in the `figs/` directory:

- `figs/Fig3E_left_organwise_enrichment.svg`
- `figs/Fig3E_left_organwise_enrichment_600dpi.png`

The script creates the `figs/` directory automatically if it does not already exist.

---

## Required Python packages
The script requires the following Python packages:

- `pandas`
- `numpy`
- `matplotlib`

---

## Example run
From the directory containing `Fig3e_left_enrichment.py`, run:

```bash
python3 Fig3e_left_enrichment.py
```

##Processing details

Input table

The input CSV is expected to contain at least the following columns:

* motif_family
* organ_name
* enrichment_ratio
* qvalue

##Motif-defined sets

The script uses the historical file labels stored in the motif_family column:

* STLHQ_family
* STFHQ_family

In the manuscript framing, these are interpreted as motif-defined peptide sets rather than peptide families.

##Significance filtering

Only rows satisfying:

* qvalue < 0.05

are retained for plotting.

Plotting rule

For the STLHQ motif-defined set:

* significant organs are ranked by enrichment_ratio
* the top 12 significant organs are plotted

For the STFHQ motif-defined set:

* all significant organs are ranked by enrichment_ratio
* all significant organs are plotted

##Enrichment display

The x-axis shows:

* enrichment_ratio on a logarithmic scale

Values are clipped internally to a minimum positive value (1e-12) before plotting, to avoid issues with log scaling.

##Panel structure

The output figure contains two horizontal bar-plot panels:

* left: STLHQ motif-defined set
* right: STFHQ motif-defined set

Both panels share the same x-axis limits for direct visual comparison.

⸻

##Notes

* The file names and motif_family values retain the historical label “family,” but in this study these sets are interpreted as motif-defined peptide sets rather than peptide families.
* This script reproduces the processed enrichment panel only; it does not compute enrichment ratios or q-values upstream.
* The input table is assumed to be a processed summary table derived from prior organ-wise enrichment analysis.


⸻

##Directory structure
Fig3/
├── Fig3e_left_enrichment.py
├── README_Fig3e_left.md
├── data/
│   └── small_CPM_summary_table.csv
└── figs/