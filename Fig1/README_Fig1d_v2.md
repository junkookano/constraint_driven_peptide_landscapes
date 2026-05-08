# README_Fig1d

## Purpose
This script reproduces **Fig. 1d** of the manuscript, which shows the parenchyma UMAP embedding.


## Overview
The script performs the following steps:

1. Loads the parenchyma count matrix from a wide-format CSV table.
2. Detects organ/subtype columns named like `1a`, `1b`, `2a`, etc.
3. Applies preprocessing:
   - non-numeric values converted to 0
   - negative values clipped to 0
   - all-zero rows removed
   - `log1p` transformation
   - row-wise normalization
   - zero-variance column removal
4. Performs PCA and UMAP using the 9/18 settings.
5. Assigns:
   - **color** = dominant organ number
   - **marker shape** = subtype of the maximum-valued column
6. Saves the square publication-style panel used for Fig. 1d.
7. Saves embedding and mapping files for downstream use.

---
## Script
`Fig1d_parenchyma_panel.py`

## Input files
Place the following files in the `data/` directory located in the same folder as the script:

- `data/parenchyma.csv`
- `data/color_of.json` (optional, but recommended if you want to preserve the manuscript color scheme as closely as possible)

**Note:** The input filename corresponds to the processed table used for the final figure generation.
---

## Output files
Running the script generates the following files.

### Figure outputs
- `figs/Fig1d_parenchyma_panel_square.png`
- `figs/Fig1d_parenchyma_panel_square.pdf`

### Optional legend-only outputs
If the legend-only block is included in the script, it also generates:
- `figs/Fig1d_parenchyma_legend_only.png`
- `figs/Fig1d_parenchyma_legend_only.pdf`

### Embedding / model outputs
- `results/parenchyma_umap_cosine.npy`
- `models/parenchyma_umap_cosine.pkl`
- `results/parenchyma_umap_cosine.csv`

---

## Required Python packages
The script requires the following Python packages:

- `pandas`
- `numpy`
- `matplotlib`
- `scikit-learn`
- `umap-learn`
- `joblib`

---

## Example run
From the directory containing `Fig1d_parenchyma_panel.py`, run:

```bash
python3 Fig1d_parenchyma_panel.py
```

## Processing details

Input table structure

The input parenchyma.csv is expected to be a wide-format table with:

* one character column
* multiple organ/subtype columns named like:
    * 1a, 1b, 1c
    * 2a, 2b
    * …
    * 34a, 34b, 34c

The numeric portion indicates the organ number, and the alphabetic suffix indicates the subtype.

## Preprocessing

The script uses the following preprocessing workflow:

* invalid numeric entries are coerced to 0
* negative values are clipped to 0
* rows with zero total abundance are removed
* values are transformed with log1p
* row-wise normalized values are used for embedding
* zero-variance columns are excluded before PCA

## Embedding settings

The parenchyma UMAP is generated using:

* PCA with up to 10 components
* UMAP with:
    * n_neighbors = 30
    * min_dist = 0.2
    * metric = "cosine"
    * random_state = 42
    * low_memory = True
    * init = "spectral"
    * n_components = 2

## Color and marker assignment

For each peptide row:

* the dominant organ number is defined as the organ number whose associated subtype columns have the largest row-wise summed value
* the subtype marker is defined by the single maximum-valued retained column for that row

Thus:

* color encodes organ number
* marker shape encodes subtype

## Legend policy

The publication-style panel itself is saved without legends.


⸻

## Notes

* The square panel version is intended for manuscript use.
* The main Fig. 1d panel and the legend may be handled separately during figure assembly.
* color_of.json is used when available; otherwise fallback matplotlib palettes are used.
* The exact mapping of subtype codes (for example a–n) is documented separately in the Extended Data table.



⸻

## Directory structure
Fig1/
├── Fig1d_parenchyma_panel.py
├── README_Fig1d.md
├── data/
│   ├── parenchyma.csv
│   └── color_of.json
├── figs/
├── results/
└── models/
