# README_Fig3c

## Purpose
This script reproduces **Fig. 3c** of the manuscript, which shows the organ-by-layer enrichment heatmaps for the STLHQ and STFHQ motif-defined peptide sets.



## Overview
The script performs the following steps:

1. Loads the merged capillary/parenchyma peptide CPM table.
2. Defines motif families using fixed regex patterns:
   - `^STLHQ..$`
   - `^STFHQ..$`
3. Selects peptides matching each motif family.
4. Sums CPM values within each `organ_name × layer` combination.
5. Transforms the summed CPM values using `log1p`.
6. Creates organ-by-layer heatmaps for the top-ranked organs.
7. Saves one heatmap panel for each motif family.

---
## Script
`Fig3c_heatmap.py`

## Input file
Place the following file in the `data/` directory located in the same folder as the script:

- `data/merged_cap_par_CPM.csv`

**Note:** The input filename corresponds to the processed table used for the final figure generation.

---

## Output files
Running the script generates the following files in the `figs/` directory:

- `figs/Fig3C_Main_Top15_STLHQ_log1pCPM.svg`
- `figs/Fig3C_Main_Top15_STLHQ_log1pCPM_600dpi.png`
- `figs/Fig3C_Main_Top15_STFHQ_log1pCPM.svg`
- `figs/Fig3C_Main_Top15_STFHQ_log1pCPM_600dpi.png`

The script creates the `figs/` directory automatically if it does not already exist.

---

## Required Python packages
The script requires the following Python packages:

- `pandas`
- `numpy`
- `matplotlib`

---

## Example run
From the directory containing `Fig3c_heatmap.py`, run:

```bash
python3 Fig3c_heatmap.py
```

##Processing details

Input table

The input CSV is expected to contain at least the following columns:

* organ_name
* layer
* character
* CPM

##Layer handling

The script normalizes layer values to lowercase and processes two expected layers:

* capillary
* parenchyma

If one of these layers is absent after pivoting for a given motif family, the missing column is created and filled with 0.0 so that the heatmap layout remains consistent.

##Motif family definitions

The following fixed motif-family regex definitions are used:

* STLHQ: ^STLHQ..$
* STFHQ: ^STFHQ..$

These definitions select 7-mer peptide subsets for downstream aggregation.

##Aggregation rule

For each motif family:

1. peptides matching the regex are selected
2. CPM values are summed within each organ_name × layer group
3. the grouped sums are transformed as:

* log1p(CPM)

The resulting values are arranged into a pivot table with:

* rows = organ_name
* columns = layer

##Organ ranking

Organs are ranked using:

* rank_score = max(capillary, parenchyma)

The top 15 ranked organs are displayed in each heatmap panel.

##Heatmap scaling

Each heatmap is plotted using:

* colormap: YlGnBu
* vmin = 0
* vmax = 95th percentile of positive values within that panel

Thus, the upper color scale is determined separately for each motif family panel.

##Figure elements

Each output panel contains:

* rows = top 15 organs/microenvironments
* columns = Capillary and Parenchyma
* color bar labeled log1p(CPM)

⸻

##Notes

* This script reproduces the main heatmap panels only; it does not identify motifs or medoids upstream.
* The motif-family definitions are fixed in the script and correspond to the families used in the manuscript.
* The displayed values are based on summed CPM per organ/layer, transformed by log1p.
* Because the top organs are ranked independently for each motif family, the row sets may differ between the STLHQ and STFHQ panels.

⸻

##Directory structure
Fig3/
├── Fig3c_heatmap.py
├── README_Fig3c.md
├── data/
│   └── merged_cap_par_CPM.csv
└── figs/