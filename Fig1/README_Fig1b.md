# README_Fig1b

## Purpose
This script reproduces the bulk-organ UMAP embedding shown in **Fig. 1b** of the manuscript. The legend used in the final assembled figure is not reproduced in this script.

## Script
`Fig1b_bulk.py`

## Input file
Place the following file in the `data/` directory located in the same folder as the script:

- `data/41organs_112525.csv`

**Note:** Input files correspond to the processed tables used to generate the final figure panel.

## Output files
Running the script generates the following files in the `figs/` directory:

- `figs/Fig1b_bulk_UMAP_system.svg`
- `figs/Fig1b_bulk_UMAP_system_600dpi.png`

The script also creates the `figs/` and `results/` directories automatically if they do not already exist.

## Required Python packages
The script requires the following Python packages:

- `pandas`
- `numpy`
- `scikit-learn`
- `umap-learn`
- `matplotlib`

## Example run
From the directory containing `Fig1b_bulk.py`, run:

```bash
python3 Fig1b_bulk.py
```

##Processing summary

The script performs the following steps:

1. Loads the bulk organ count matrix from 41organs_112525.csv.
2. Extracts organ columns corresponding to labels B through AP.
3. Assigns each peptide row to its dominant organ based on the maximum count across organ columns.
4. Maps dominant organs to organ systems for coloring.
5. Applies the embedding pipeline:
    * log1p transformation
    * row-wise normalization
    * PCA (n_components = min(10, number of retained columns))
    * UMAP (n_neighbors=30, min_dist=0.2, metric="cosine", random_state=42)
6. Generates a square UMAP scatter plot colored by organ system.

Notes

* Rows with zero total signal after log transformation are excluded before embedding.
* Columns with zero variance after normalization are excluded before PCA.
* If multiple organs share the same maximum value in a row, the first one returned by argmax is used as the dominant organ.
* Organ-system colors are hard-coded in the script.
* This script is intended to reproduce the visualization for Fig. 1b only.

Directory structure

An example directory structure is shown below
Fig1/
├── Fig1b_bulk.py
├── README_Fig1b.md
├── data/
│   └── 41organs_112525.csv
├── figs/
└── results/