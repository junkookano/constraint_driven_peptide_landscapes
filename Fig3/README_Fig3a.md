# README_Fig3a

## Purpose
This script reproduces **Fig. 3a** of the manuscript, which shows the capillary and parenchyma UMAP panels with the corresponding medoid positions.


## Overview
The script performs the following steps:

1. Loads the capillary UMAP embedding table.
2. Loads the parenchyma UMAP embedding table.
3. Uses previously identified fixed medoid coordinates for each panel.
4. Draws the capillary and parenchyma panels side by side.
5. Plots the medoid positions on the corresponding embeddings.
6. Saves the panel figure.

---
## Script
`Fig3a_medoid.py`


## Input files
Place the following files in the `data/` directory located in the same folder as the script:

- `data/df_capillary_pancreasFixed_umap_hdbscan_mcs50.csv`
- `data/parenchyma_HDBSCAN_with_character.csv`

**Note:** The input filename corresponds to the processed table used for the final figure generation.

---

## Output files
Running the script generates the following files in the `figs/` directory:

- `figs/Fig3A_cap_par_medoids.svg`
- `figs/Fig3A_cap_par_medoids_600dpi.png`

The script also creates the `figs/` directory automatically if it does not already exist.

---

## Required Python packages
The script requires the following Python packages:

- `pandas`
- `numpy`
- `matplotlib`

---

## Example run
From the directory containing `Fig3a_medoid.py`, run:

```bash
python3 Fig3a_medoid.py
```

##Processing details

Input embeddings

The script expects both input CSV files to contain at least the following columns:

* UMAP1
* UMAP2

These files are treated as processed embedding tables.

Medoid plotting

The script does not recompute medoids.

Instead, it plots previously identified fixed medoid coordinates used for the manuscript figure.

In the current version of the script, the medoids are:

* capillary medoid: STLHQEL
* parenchyma medoid: STFHQKL

The medoid coordinates are supplied directly in the script and overlaid on the corresponding embeddings.

Panel rendering

The script:

* plots all embedding points in light gray as the background
* overlays the fixed medoid positions as black points
* renders the capillary and parenchyma panels side by side
* uses matched axis limits for visual consistency between panels

⸻

##Notes

* This script reproduces the panel visualization for Fig. 3a.
* Medoid identification was performed upstream and is described in the Methods.
* Fixed medoid coordinates are used here to preserve consistency with the manuscript figure.
* The script is intended for figure reproduction and does not rerun the medoid-identification workflow.


⸻

##Directory structure
Fig3/
├── Fig3a_medoid.py
├── README_Fig3a.md
├── data/
│   ├── df_capillary_pancreasFixed_umap_hdbscan_mcs50.csv
│   └── parenchyma_HDBSCAN_with_character.csv
└── figs/