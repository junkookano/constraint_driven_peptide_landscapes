# README_Fig3b

## Purpose
This script reproduces **Fig. 3b** of the manuscript, which shows the Tier0 sequence logo panels for the STLHQ and STFHQ motif-defined peptide sets in the capillary and parenchymal layers.


## Overview
The script performs the following steps:

1. Loads the merged capillary/parenchyma peptide table.
2. Separates rows by layer (`capillary` or `parenchyma`).
3. Defines Tier0 peptide sets using fixed motif regex patterns:
   - `^STLHQ..$`
   - `^STFHQ..$`
4. Builds a **layer-specific read-weighted amino-acid background**.
5. Builds **read-weighted positional amino-acid counts** from the Tier0 subset.
6. Computes a **log2-odds position-specific scoring matrix (PSSM)** relative to the layer background.
7. Clips negative log-odds values to zero to generate **positive-only sequence logos**.
8. Saves one logo panel for each motif/layer combination using a common y-axis scale across all panels.

---
## Script
`Fig3b_logo.py`

## Input file
Place the following file in the `data/` directory located in the same folder as the script:

- `data/merged_cap_par_CPM.csv`

**Note:** The input filename corresponds to the processed table used for the final figure generation.

---

## Output files
Running the script generates the following files in the `figs/` directory:

- `figs/Fig3B_Tier0_STLHQ_capillary_logo_posonly_fixedscale.svg`
- `figs/Fig3B_Tier0_STLHQ_capillary_logo_posonly_fixedscale_600dpi.png`
- `figs/Fig3B_Tier0_STLHQ_parenchyma_logo_posonly_fixedscale.svg`
- `figs/Fig3B_Tier0_STLHQ_parenchyma_logo_posonly_fixedscale_600dpi.png`
- `figs/Fig3B_Tier0_STFHQ_capillary_logo_posonly_fixedscale.svg`
- `figs/Fig3B_Tier0_STFHQ_capillary_logo_posonly_fixedscale_600dpi.png`
- `figs/Fig3B_Tier0_STFHQ_parenchyma_logo_posonly_fixedscale.svg`
- `figs/Fig3B_Tier0_STFHQ_parenchyma_logo_posonly_fixedscale_600dpi.png`

The script creates the `figs/` directory automatically if it does not already exist.

---

## Required Python packages
The script requires the following Python packages:

- `pandas`
- `numpy`
- `matplotlib`
- `logomaker`

---

## Example run
From the directory containing `Fig3b_logo.py`, run:

```bash
python3 Fig3b_logo.py
```

##Processing details

Input table

The input CSV is expected to contain at least the following columns:

* character
* layer
* reads

##Layer handling

The script normalizes layer values to lowercase and processes the two layers separately:

* capillary
* parenchyma

##Tier0 motif definitions

The following fixed Tier0 motif definitions are used:

* STLHQ: ^STLHQ..$
* STFHQ: ^STFHQ..$

These definitions select 7-mer peptide subsets used for panel generation.

##Background model

For each layer, a read-weighted amino-acid background is computed from all peptides in that layer.

This background is used as the denominator for log-odds calculation.

##Positional counts

For each motif/layer combination, positional amino-acid counts are computed from the Tier0 peptide subset after aggregating reads by unique peptide sequence.

Thus, the logos are based on:

* read-weighted
* sequence-aggregated
* position-specific

counts.

##PSSM and logo generation

A position-specific scoring matrix (PSSM) is computed as:

* log2( motif_position_frequency / layer_background_frequency )

with a pseudocount of 0.5.

Negative log-odds values are clipped to zero, so the plotted logos are positive-only log-odds logos.

Shared y-axis scaling

All motif/layer panels share a common y-axis upper limit, defined as the maximum positive log-odds value observed across all generated panels, multiplied by 1.05.

This allows direct visual comparison across panels.

##Figure elements

Each output panel contains:

* x-axis positions 1–7
* y-axis labeled log2-odds
* positive-only sequence logo letters
* no panel title in the publication-style output

⸻

##Notes

* This script reproduces the logo panels only; it does not identify medoids or discover motif families upstream.
* The motif definitions are fixed in the script and correspond to the Tier0 peptide sets used in the manuscript.
* The logos are computed relative to the full layer-specific amino-acid background, not a global combined background.

⸻

##Directory structure
Fig3/
├── Fig3b_logo.py
├── README_Fig3b.md
├── data/
│   └── merged_cap_par_CPM.csv
└── figs/