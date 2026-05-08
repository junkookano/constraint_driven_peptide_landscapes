# README_Fig1c

## Purpose
These scripts reproduce **Fig. 1c** of the manuscript, which shows the capillary UMAP embedding and the final organ-colored capillary panel.

## Overview
Fig. 1c is reproduced in three steps:

1. **Pancreas label decision**
   - compares pancreas-related labels 11 and 37
   - assigns a pancreas-fixed label column for downstream use

2. **Capillary preprocessing and embedding generation**
   - aligns the raw capillary count matrix to the metadata table by peptide character
   - merges column 37 into column 11
   - applies preprocessing, PCA, and UMAP
   - generates the processed capillary embedding table

3. **Final panel rendering**
   - reads the processed capillary table with fixed UMAP coordinates
   - applies organ colors
   - renders the square manuscript panel for Fig. 1c

---

## Scripts

### 1. `Fig1c_pancreas_label_decision.py`
This script compares capillary pancreas-related labels **11** and **37** using:

- exact Jaccard overlap
- Hamming-distance-1 fuzzy overlap
- position-wise PWM correlation
- a simple heuristic decision rule

It writes a new column, `organ_label_pancreas_fixed`, to the output table.

### 2. `Fig1c_capillary_preprocess_and_embedding.py`
This script generates the capillary UMAP embedding used for Fig. 1c by:

- loading the pancreas-fixed metadata table
- loading the raw capillary count matrix
- aligning rows by `character`
- merging count column **37** into column **11**
- applying `log1p` transformation and row-wise normalization
- removing zero-variance columns
- performing PCA (`n_components = 10` or fewer)
- performing UMAP with the 9/18 settings

### 3. `Fig1c_capillary_panel.py`
This script renders the final capillary UMAP panel from the processed capillary table with fixed UMAP coordinates and pancreas-fixed organ labels.

A square publication-style version is also used for manuscript panel replacement.

---

## Input files

Place the following files in the `data/` directory located in the same folder as the scripts.

### Required for `Fig1c_pancreas_label_decision.py`
- `data/df_normal_capillary_unsup_umap_hdbscan_cosine_mcs50.csv`

### Required for `Fig1c_capillary_preprocess_and_embedding.py`
- `data/df_capillary_pancreas_fixed.csv`
- `data/normal_capillary.csv`

### Required for `Fig1c_capillary_panel.py`
- `data/df_capillary_pancreasFixed_withOrganName.csv`
- `data/color_of.json` (optional, but recommended for reproducing the manuscript panel colors)

**Note:** The input filename corresponds to the processed table used for the final figure generation.

---

## Output files

### `Fig1c_pancreas_label_decision.py`
- `results/df_capillary_pancreas_fixed.csv`

### `Fig1c_capillary_preprocess_and_embedding.py`
- `results/df_capillary_pancreasFixed_unsupUMAP_cosine.csv`
- `results/umap_capillary_pancreasFixed_unsup_cosine.npy`
- `models/umap_capillary_pancreasFixed_unsup_cosine.pkl`

### `Fig1c_capillary_panel.py`
Depending on the version used, the script generates one or more of the following:


- `figs/Fig1c_capillary_panel_square.png`
- `figs/Fig1c_capillary_panel_square.pdf`

---

## Example run

Run the scripts in the following order from the directory containing the scripts:

```bash
python3 Fig1c_pancreas_label_decision.py
python3 Fig1c_capillary_preprocess_and_embedding.py
python3 Fig1c_capillary_panel.py
```

## Processing details

Pancreas-related label handling

Capillary pancreas-related labels 11 and 37 were compared computationally.

The notebook-derived decision step reported:

* #11 n = 362
* #37 n = 465
* exact Jaccard overlap = 0.000
* fuzzy Hamming-distance-1 overlap ≈ 0
* PWM position-wise mean Pearson correlation = 0.901

Based on this comparison, label 11 was retained and label 37 was collapsed into label 11 for downstream capillary analysis.

Embedding settings

The capillary UMAP was generated using:

* log1p transformation
* row-wise normalization
* zero-variance column removal
* PCA with up to 10 components
* UMAP with:
    * n_neighbors = 30
    * min_dist = 0.2
    * metric = "cosine"
    * random_state = 42
    * init = "spectral"
    * n_components = 2

##Panel rendering

The final panel uses:

* fixed UMAP coordinates from the processed capillary table
* pancreas-fixed organ labels
* colors from color_of.json when available
* fallback matplotlib palettes otherwise

##Notes

* Fig. 1c required pancreas-related label correction before embedding generation.
* The processed capillary table used for panel rendering contains fixed UMAP coordinates.
* The final panel is rendered from the processed capillary table, not directly from the raw count matrix.
* Colors are assigned using color_of.json when available.
* The square panel version is intended for manuscript use.


##Directory structure

Fig1/
├── Fig1c_pancreas_label_decision.py
├── Fig1c_capillary_preprocess_and_embedding.py
├── Fig1c_capillary_panel.py
├── README_Fig1c.md
├── data/
│   ├── df_normal_capillary_unsup_umap_hdbscan_cosine_mcs50.csv
│   ├── df_capillary_pancreas_fixed.csv
│   ├── normal_capillary.csv
│   ├── df_capillary_pancreasFixed_withOrganName.csv
│   └── color_of.json
├── results/
├── models/
└── figs/