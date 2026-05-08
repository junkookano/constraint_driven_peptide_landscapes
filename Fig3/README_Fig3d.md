# README_Fig3d

## Purpose
These scripts reproduce **Fig. 3d** of the manuscript, which shows the PSSM heatmap panels for the STLHQ and STFHQ motif families.

## Overview
Fig. 3d is reproduced in two steps:

1. **PSSM generation**
   - extracts motif-defined peptide subsets
   - computes read-weighted counts and frequencies
   - converts frequencies to log-odds PSSM matrices

2. **PSSM heatmap rendering**
   - loads the precomputed log-odds PSSM matrices
   - renders the two-panel heatmap figure for STLHQ and STFHQ

---

## Scripts

### 1. `Fig3d_pssm_generation.py`
This script generates the PSSM tables for the two motif families:

- `STLHQ_defined peptide set`
- `STFHQ_defined peptide set`

It produces:

- read-weighted counts matrices
- read-weighted frequency matrices
- log-odds PSSM matrices

### 2. `Fig3d_pssm_heatmap.py`
This script reads the precomputed log-odds PSSM matrices and renders the final two-panel Fig. 3d heatmap figure.

---

## Input files

### Required for `Fig3d_pssm_generation.py`
Place the following file in the `data/` directory located in the same folder as the script:

- `data/phase2.6_motif_family_subset_reads20.csv`

### Required for `Fig3d_pssm_heatmap.py`
Place the following files in the `data/` directory located in the same folder as the script:

- `data/STLHQ_family_PSSM_logodds.csv`
- `data/STFHQ_family_PSSM_logodds.csv`

**Note:** The input filename corresponds to the processed table used for the final figure generation.

---

## Output files

### `Fig3d_pssm_generation.py`
This script generates the following CSV files in the `results/` directory:

- `results/STLHQ_family_PSSM_counts.csv`
- `results/STLHQ_family_PSSM_freq.csv`
- `results/STLHQ_family_PSSM_logodds.csv`
- `results/STFHQ_family_PSSM_counts.csv`
- `results/STFHQ_family_PSSM_freq.csv`
- `results/STFHQ_family_PSSM_logodds.csv`

If the optional sequence-logo block is retained in the script, additional logo files may also be generated in the `figs/` directory.

### `Fig3d_pssm_heatmap.py`
This script generates the following files in the `figs/` directory:

- `figs/Fig3D_PSSM_heatmap_STLHQ_STFHQ_sharedCB.svg`
- `figs/Fig3D_PSSM_heatmap_STLHQ_STFHQ_sharedCB_600dpi.png`

---

## Required Python packages

### For `Fig3d_pssm_generation.py`
- `pandas`
- `numpy`
- `matplotlib`
- `logomaker`

### For `Fig3d_pssm_heatmap.py`
- `pandas`
- `numpy`
- `matplotlib`

---

## Example run
Run the scripts in the following order from the directory containing the scripts:

```bash
python3 Fig3d_pssm_generation.py
python3 Fig3d_pssm_heatmap.py
```

##Processing details

PSSM generation

For each motif-defined peptide set (STLHQ_motif and STFHQ_motif), the script:

1. filters rows from phase2.6_motif_family_subset_reads20.csv
2. aggregates identical peptide sequences by read count
3. constructs a position-by-amino-acid count matrix
4. converts the count matrix into a frequency matrix
5. computes a log-odds PSSM matrix

The amino-acid alphabet is fixed as:

* ACDEFGHIKLMNPQRSTVWY

Read weighting

Both counts and frequencies are computed in a read-weighted manner.

Thus, peptide sequences with larger read counts contribute proportionally more to the resulting PSSM matrices.

Background definition

For the PSSM generation step used for Fig. 3d, log-odds values are computed relative to a uniform 20-amino-acid background, assuming:

* background frequency = 1/20 for each amino acid

This differs from the layer-specific background used for the positive-only logo panels in Fig. 3b.

Heatmap input format

The heatmap-rendering script expects each log-odds CSV to have:

* rows = positions
* columns = amino acids

with position indices corresponding to the seven positions of the 7-mer motif.

Heatmap rendering

The final heatmap panel:

* loads the STLHQ and STFHQ log-odds matrices
* reorders amino acids using the fixed alphabet order
* converts the matrices into amino-acid × position format
* applies one shared diverging color scale across both panels
* uses a common color bar labeled log-odds score

Color scaling

The shared color scale is defined from the combined values of both PSSM matrices using:

* the 98th percentile of the absolute log-odds values

This value is used symmetrically as:

* vmin = -maxabs
* vmax = +maxabs

⸻

##Notes

*The output file names retain the historical label “family,” but in this study these sets are interpreted as motif-defined peptide sets rather than peptide families.
* The PSSM generation script computes the upstream matrices used to create Fig. 3d.
* The heatmap-rendering script reproduces the final panel visualization only.
* The background model used here is a uniform 20-amino-acid background, not a layer-specific empirical background.
* This background choice is specific to Fig. 3d and differs from the sequence-logo calculation used for Fig. 3b.


⸻

##Directory structure
Fig3/
├── Fig3d_pssm_generation.py
├── Fig3d_pssm_heatmap.py
├── README_Fig3d.md
├── data/
│   ├── phase2.6_motif_family_subset_reads20.csv
│   ├── STLHQ_family_PSSM_logodds.csv
│   └── STFHQ_family_PSSM_logodds.csv
├── results/
└── figs/