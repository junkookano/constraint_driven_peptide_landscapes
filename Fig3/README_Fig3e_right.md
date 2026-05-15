# README_Fig3e_right

## Purpose
This script reproduces the **right-side panel of Fig. 3e** of the manuscript, which shows convergence scores for predefined interface organs.


## Overview
The script performs the following steps:

1. Loads a processed summary table of organ-wise enrichment statistics.
2. Extracts enrichment-ratio columns corresponding to the historical labels:
   - `STLHQ_family`
   - `STFHQ_family`
3. Selects a predefined set of interface organs.
4. Computes a convergence score for each interface organ.
5. Plots the resulting convergence scores as a horizontal bar plot.
6. Saves the figure.

---
## Script
`Fig3e_right.py`

## Input file
Place the following file in the `data/` directory located in the same folder as the script:

- `data/small_CPM_summary_table.csv`

**Note:** The input filename corresponds to the processed table used for the final figure generation.

---

## Output files
Running the script generates the following files in the `figs/` directory:

- `figs/Fig3E_right_interface_organ_convergence.svg`
- `figs/Fig3E_right_interface_organ_convergence_600dpi.png`

The script creates the `figs/` directory automatically if it does not already exist.

---

## Required Python packages
The script requires the following Python packages:

- `pandas`
- `matplotlib`

---

## Example run
From the directory containing `Fig3e_right.py`, run:

```bash
python3 Fig3e_right.py
```

##Processing details

Input table

The input CSV is expected to contain at least the following columns:

* motif_family
* organ_name
* enrichment_ratio

##Historical motif labels

The script uses the historical labels stored in the motif_family column:

* STLHQ_family
* STFHQ_family

In the manuscript framing, these are interpreted as motif-defined peptide sets rather than peptide families.

##Pivot and extraction

The input table is reshaped into a wide-format table in which each row corresponds to an organ_name, and enrichment-ratio columns are extracted separately for the STLHQ and STFHQ motif-defined sets.

##Predefined interface organs

The convergence plot is restricted to the following interface organs:

* liver_bile_ductal_cells
* spleen_red_pulp
* appendix_mucosa_epithelial_cells
* anterior_pituitary_gland

##Convergence score

For each predefined interface organ, the plotted value is:

* convergence_score = ER_STLHQ × ER_STFHQ

where:

* ER_STLHQ = enrichment ratio for the STLHQ motif-defined set
* ER_STFHQ = enrichment ratio for the STFHQ motif-defined set

##Figure elements

The script produces a horizontal bar plot in which:

* y-axis = predefined interface organs
* x-axis = convergence score

Organs are sorted in ascending order of convergence score before plotting.

⸻

Notes

* The file names and motif_family values retain the historical label “family,” but in this study these sets are interpreted as motif-defined peptide sets rather than peptide families.
* This script reproduces the processed right-side convergence panel only; it does not compute enrichment ratios, q-values, or interface-organ definitions upstream.
* The predefined interface-organ list is fixed in the script and corresponds to the organs highlighted in the manuscript figure.

⸻

Directory structure

Fig3/
├── Fig3e_right.py
├── README_Fig3e_right.md
├── data/
│   └── small_CPM_summary_table.csv
└── figs/