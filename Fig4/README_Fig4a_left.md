# README_Fig4a_left

## Purpose
This script reproduces the **left-side panel of Fig. 4a** of the manuscript, which shows the global UMAP embedding with fixed highlighted coordinates for `STLHQEL`, `STFHQKL`, and `EVGTARY`.


## Overview
The script performs the following steps:

1. Loads the processed global embedding table.
2. Plots all embedding points as a light-gray background.
3. Overlays three fixed highlighted peptide coordinates:
   - `STLHQEL`
   - `STFHQKL`
   - `EVGTARY`
4. Saves the resulting panel figure.

---
## Script
`Fig4a_left.py`

## Input file
Place the following file in the `data/` directory located in the same folder as the script:

- `data/merged_cap_par_CPM.csv`

**Note:** The input filename corresponds to the processed table used for the final figure generation.
---

## Output files
Running the script generates the following files in the `figs/` directory:

- `figs/Fig4A_left_global_UMAP_fixed_points.svg`
- `figs/Fig4A_left_global_UMAP_fixed_points_600dpi.png`

The script creates the `figs/` directory automatically if it does not already exist.

---

## Required Python packages
The script requires the following Python packages:

- `pandas`
- `matplotlib`

---

## Example run
From the directory containing `Fig4a_left.py`, run:

```bash
python3 Fig4a_left.py
```

##Processing details

##Input embedding

The input CSV is expected to contain at least the following columns:

* UMAP1
* UMAP2

The table is treated as a processed global embedding table.

##Background points

All rows in the embedding table are plotted as low-opacity light-gray points to show the global embedding structure.

Highlighted fixed coordinates

The script overlays three peptide points using fixed coordinates provided directly in the script:

* STLHQEL
* STFHQKL
* EVGTARY

These coordinates are not recomputed in this script.

##Panel rendering

The panel is rendered as:

* a square plotting area
* no tick labels
* no grid
* a global embedding background
* three highlighted labeled peptide points

⸻

##Notes

* This script reproduces the panel visualization only.
* The highlighted peptide coordinates are fixed values provided in the script and are not recomputed here.
* The script is intended for figure reproduction rather than upstream point-identification analysis.


⸻

##Directory structure
Fig4/
├── Fig4a_left.py
├── README_Fig4a_left.md
├── data/
│   └── merged_cap_par_CPM.csv
└── figs/