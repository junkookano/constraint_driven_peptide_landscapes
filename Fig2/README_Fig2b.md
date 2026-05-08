# README_Fig2b

## Purpose
This script reproduces **Fig. 2b** of the manuscript, which shows the heatmap of organ-specific enrichment values for the top cerebrum-enriched peptides in the bulk R1/R3 analysis.


## Overview
The script performs the following steps:

1. Loads the processed bulk R1/R3 digital subtraction table.
2. Selects peptides with positive `subtraction_score`.
3. Sorts them in descending order of `subtraction_score`.
4. Retains the top 50 peptides.
5. Extracts enrichment values for:
   - cerebrum
   - liver
   - skeletal muscle
6. Draws a heatmap of the top 50 peptides across these three organs.

---
## Script
`Fig2b_heatmap.py`

## Input file
Place the following file in the `data/` directory located in the same folder as the script:

- `data/bulk_R1R3_enrichment_Fig2_input_top3000.csv`

**Note:** The input filename corresponds to the processed table used for the final figure generation. The input CSV is a reduced, processed table containing the top 3000 ranked sequences used to generate Fig. 2b. The full processed digital subtraction table is not included in this repository because of file-size constraints and is described in the manuscript Data availability statement.

---

## Output files
Running the script generates the following files in the `figs/` directory:

- `figs/Fig2B_digital_subtraction_heatmap_top50.svg`
- `figs/Fig2B_digital_subtraction_heatmap_top50_600dpi.png`

The script creates the `figs/` directory automatically if it does not already exist.

---

## Required Python packages
The script requires the following Python packages:

- `pandas`
- `matplotlib`

---

## Example run
From the directory containing `Fig2b_heatmap.py`, run:

```bash
python3 Fig2b_heatmap.py
```


##Processing details

Input table

The input CSV is expected to contain at least the following columns:

* character
* subtraction_score
* E_cortex
* E_liver
* E_skeletal_muscle

##Selection rule

Only rows with:

* subtraction_score > 0

are retained.

These rows are then sorted by:

* subtraction_score in descending order

The top 50 peptides are used for plotting.

##Heatmap values

The heatmap uses the following enrichment columns:

* E_cortex
* E_liver
* E_skeletal_muscle

For figure display, E_cortex is relabeled as:

* E_cerebrum internally
* Cerebrum on the x-axis

##Plot settings

The heatmap uses:

* colormap: YlGnBu
* fixed color scale:
    * vmin = 6
    * vmax = 9

The y-axis lists peptide 7-mer sequences, with rank 1 positioned at the top of the heatmap.

##Figure elements

The script produces:

* a heatmap of the top 50 peptides
* three organ columns:
    * Cerebrum
    * Liver
    * Skeletal muscle
* a color bar labeled log2 enrichment (R3 / R1)

⸻

##Notes

* This script reproduces the processed heatmap visualization for Fig. 2b.
* The input table is assumed to be a processed digital subtraction result table, not a raw count matrix.
* The term E_cortex in the input file is displayed as Cerebrum in the figure for consistency with the manuscript.
* The color scale is intentionally fixed to allow comparison across peptides within the displayed range.
* Input filenames may be replaced with final submission filenames.

⸻

##Directory structure

Fig2/
├── Fig2b_heatmap.py
├── README_Fig2b.md
├── data/
│   └── bulk_R1R3_enrichment_full_20251205.csv
└── figs/