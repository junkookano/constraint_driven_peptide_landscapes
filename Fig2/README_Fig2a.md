# README_Fig2a

## Purpose
This script reproduces **Fig. 2a** of the manuscript, which shows the digital subtraction rank curve for the bulk R1/R3 analysis.


## Overview
The script performs the following steps:

1. Loads the processed bulk R1/R3 digital subtraction table.
2. Sorts sequences by `subtraction_score` in descending order.
3. Defines:
   - **exclusive** sequences as those with `E_max_other = 0`
   - **shared** sequences as those with `E_max_other > 0`
4. Plots the rank curve for the top-ranked sequences.
5. Marks the **first shared rank** with a vertical dashed line.
6. Draws an inset showing the transition region around the first appearance of shared sequences.

---
## Script
`Fig2a_rank_curve.py`


## Input file
Place the following file in the `data/` directory located in the same folder as the script:

- `data/bulk_R1R3_enrichment_Fig2_input_top3000.csv`

**Note:** The input filename corresponds to the processed table used for the final figure generation.
The input CSV is a reduced, processed table containing the top 3000 ranked sequences used to generate Fig. 2a. The full processed digital subtraction table is not included in this repository because of file-size constraints and is described in the manuscript Data availability statement.

---

## Output files
Running the script generates the following files in the `figs/` directory:

- `figs/Fig2A_digital_subtraction_rankcurve_bulk_R1R3.svg`
- `figs/Fig2A_digital_subtraction_rankcurve_bulk_R1R3_600dpi.png`

The script creates the `figs/` directory automatically if it does not already exist.

---

## Required Python packages
The script requires the following Python packages:

- `pandas`
- `numpy`
- `matplotlib`

---
## Example run

From the directory containing `Fig2a_rank_curve.py`, run:

```bash
python3 Fig2a_rank_curve.py
```

## Processing details



Input table

The input CSV is expected to contain at least the following columns:

* subtraction_score
* E_max_other

If present, the character column is also retained in the ranked table, but it is not required for plotting.

Ranking rule

Sequences are ranked by:

* subtraction_score in descending order

Exclusive vs shared definition

The rank curve uses the following strict definition:

* exclusive: E_max_other = 0
* shared: E_max_other > 0

The first occurrence of a shared sequence is reported as the first shared rank and indicated in the plot by a vertical dashed line.

Plot range

The main panel displays up to the top 3000 ranked sequences.

The inset focuses on the transition region:

* ranks 120–240

Figure elements

The script produces:

* a main rank-curve scatter plot
* a vertical dashed line marking the first shared rank
* a transition-region inset
* a legend distinguishing exclusive vs shared sequences

⸻

Notes

* This script reproduces the processed rank-curve visualization for Fig. 2a.
* The input table is assumed to be a processed digital subtraction result table, not a raw count matrix.
* The definition of shared sequences is intentionally strict (E_max_other > 0) and follows the digital subtraction framework used in the manuscript.


⸻

Directory structure

Fig2/
├── Fig2a_rank_curve.py
├── README_Fig2a.md
├── data/
│   └── bulk_R1R3_enrichment_full_20251205.csv
└── figs/