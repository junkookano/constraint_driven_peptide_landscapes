# README_Fig4a_right

## Purpose
This script reproduces the **right-side panel of Fig. 4a** of the manuscript, which shows the HDBSCAN cluster containing `EVGTARY` in the nervous-system embedding together with the corresponding local cluster medoid.


## Overview
The script performs the following steps:

1. Loads the processed nervous-system UMAP embedding table with HDBSCAN cluster assignments.
2. Identifies the cluster containing `EVGTARY`.
3. Extracts all points belonging to that cluster.
4. Computes the local medoid within that cluster using Euclidean distances in UMAP space.
5. Plots:
   - the cluster background points
   - `EVGTARY`
   - the local cluster medoid
6. Saves the resulting panel figure.

---
## Script
`Fig4a_right.py`


## Input file
Place the following file in the `data/` directory located in the same folder as the script:

- `data/nervous_umap_hdbscan_mcs50.csv`

**Note:** The input filename corresponds to the processed table used for the final figure generation.

---

## Output files
Running the script generates the following files in the `figs/` directory:

- `figs/Fig4A_right_EVGTARY_cluster_medoid_mapping.svg`
- `figs/Fig4A_right_EVGTARY_cluster_medoid_mapping_600dpi.png`

The script creates the `figs/` directory automatically if it does not already exist.

---

## Required Python packages
The script requires the following Python packages:

- `pandas`
- `numpy`
- `matplotlib`
- `scipy`

---

## Example run
From the directory containing `Fig4a_right.py`, run:

```bash
python3 Fig4a_right.py
```

##Processing details

##Input table

The input CSV is expected to contain at least the following columns:

* UMAP1
* UMAP2
* cluster
* peptide

The table is treated as a processed nervous-system embedding with HDBSCAN cluster assignments.

EVGTARY cluster identification

The script identifies the cluster containing EVGTARY by searching the peptide column, then retrieves the corresponding cluster ID.

All rows assigned to that cluster are extracted for downstream plotting.

Local medoid calculation

Within the EVGTARY cluster, pairwise Euclidean distances are computed in UMAP space.

The local medoid is defined as the point whose summed Euclidean distance to all other points in the same cluster is minimal.

Thus, the medoid shown in this panel is:

* cluster-local
* computed only within the EVGTARY cluster
* based on Euclidean distances in the 2D UMAP embedding

##Panel rendering

The panel shows:

* all points in the EVGTARY cluster as light-gray background points
* EVGTARY as a highlighted point with a green outline
* the local medoid as a highlighted point with a black outline

The plotting window is adjusted to a square region centered on the extracted cluster.

⸻

##Notes

* This script reproduces the panel visualization only.
* The script assumes that the nervous-system embedding and HDBSCAN clustering were generated upstream.
* The local medoid shown here is recomputed from the processed cluster coordinates in the input file.


⸻

##Directory structure
Fig4/
├── Fig4a_right.py
├── README_Fig4a_right.md
├── data/
│   └── nervous_umap_hdbscan_mcs50.csv
└── figs/