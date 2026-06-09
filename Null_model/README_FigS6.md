# README_NullModels_BulkUMAP

## Purpose
These scripts reproduce the two null models used to assess structure in the bulk-organ UMAP embedding:

1. **Null model A**: label-permuted coloring
2. **Null model B**: feature-wise shuffle

In addition, a companion script quantifies geometric differences between the observed embedding and Null model B using shared-core density and global spread from center.

---

## Scripts

### 1. `FigS6_null_A_label_permuted.py`
This script reproduces **Null model A**.

It:
- computes the bulk-organ UMAP embedding using the same preprocessing and UMAP settings as the observed data
- randomly permutes the system labels
- recolors the observed embedding using the permuted labels

Thus, Null model A preserves the real embedding geometry but destroys the correspondence between embedding position and system label.

### 2. `FigS6_null_B_featurewise_shuffle.py`
This script reproduces **Null model B**.

It:
- computes the same preprocessed feature matrix used for the observed bulk embedding
- independently shuffles each retained feature column
- reruns PCA and UMAP using the same parameters as the observed analysis
- colors the shuffled embedding using the original observed system labels

Thus, Null model B preserves the marginal distribution of each feature while disrupting row-wise multifeature structure.

### 3. `FigS6_null_B_core_spread_metrics.py`
This script quantifies two geometric summary metrics for the observed embedding and Null model B:

- **Shared-core density**
- **Global spread from center**

It also generates bar plots and summary CSV files for these metrics.

---

## Input files

### Required for `FigS6_null_A_label_permuted.py`
- `data/41organs_112525_with_system.csv`

### Required for `FigS6_null_B_featurewise_shuffle.py`
- `data/41organs_112525_with_system.csv`

### Required for `FigS6_null_B_core_spread_metrics.py`
- `data/umap_41organs_cosine_mcs50_withOrgan_with_system.csv`
- `data/umap_41organs_cosine_mcs50_nullB_feature_shuffle.csv`



---

## Output files

### `FigS6_null_A_label_permuted.py`
Saved in the `figs/` directory:

- `figs/FigS6_bulk_null_A_label_permuted.pdf`
- `figs/FigS6_bulk_null_A_label_permuted_600dpi.png`

### `FigS6_null_B_featurewise_shuffle.py`
Saved in the `figs/` directory:

- `figs/FigS6_bulk_null_B_featurewise_shuffle.pdf`
- `figs/FigS6_bulk_null_B_featurewise_shuffle_600dpi.png`

Saved in the `results/` directory:

- `results/FigS6_bulk_null_B_featurewise_shuffle_embedding.csv`

### `FigS6_null_B_core_spread_metrics.py`
Saved in the `results/` directory:

- `results/FigS6_nullB_core_spread_summary.csv`
- `results/FigS6_nullB_core_spread_sensitivity.csv`

Saved in the `figs/` directory:

- `figs/FigS6_shared_core_density.pdf`
- `figs/FigS6_shared_core_density_600dpi.png`
- `figs/FigS6_global_spread_from_center.pdf`
- `figs/FigS6_global_spread_from_center_600dpi.png`

---

## Required Python packages

### For `FigS6_null_A_label_permuted.py`
- `pandas`
- `numpy`
- `matplotlib`
- `scikit-learn`
- `umap-learn`

### For `FigS6_null_B_featurewise_shuffle.py`
- `pandas`
- `numpy`
- `matplotlib`
- `scikit-learn`
- `umap-learn`

### For `FigS6_null_B_core_spread_metrics.py`
- `pandas`
- `numpy`
- `matplotlib`

---

## Example run
Run the scripts in the following order from the directory containing the scripts:

```bash
python3 FigS6_null_A_label_permuted.py
python3 FigS6_null_B_featurewise_shuffle.py
python3 FigS6_null_B_core_spread_metrics.py
```

##Processing details
##Observed-data preprocessing
Both Null model A and Null model B use the same observed bulk-organ preprocessing workflow as the real-data panel, including:

numeric conversion of organ columns
log1p transformation
row-wise normalization
zero-variance column removal
PCA with up to 10 components
UMAP with:
n_neighbors = 30
min_dist = 0.2
metric = "cosine"
random_state = 42
low_memory = True
init = "spectral"

##Null model A: label-permuted coloring

Null model A preserves the observed embedding coordinates and randomly permutes the system labels before coloring the points.

This tests whether the apparent spatial organization of systems could arise from arbitrary label assignment on the same geometry.

##Null model B: feature-wise shuffle

Null model B independently shuffles each retained feature column across rows before PCA/UMAP.

This preserves the marginal distribution of each feature but destroys the multifeature structure associated with each peptide row.

The shuffled embedding is then colored using the original observed system labels.

##Shared-core density

For the Null model B geometry summary, the real-data center is defined by the median coordinates of the observed embedding.

The shared-core radius is defined as:

the 10% quantile of the observed-distance distribution

The core-in fraction is then measured for both the observed embedding and Null model B relative to this same real-data core.

##Global spread from center

The global spread metric is defined as:

*the median Euclidean distance from the observed-data center

This is computed for both the observed embedding and Null model B.

##Sensitivity analysis

For Null model B, the script also evaluates additional shared-core definitions using:

*q = 0.05
*q = 0.10
*q = 0.15

and writes the results to a separate sensitivity CSV file.

⸻
##Notes
*These scripts reproduce the null-model panels and quantitative summaries for the bulk-organ embedding analysis.
*Null model A preserves the observed embedding but randomizes label assignment.
*Null model B preserves per-feature marginal distributions but disrupts row-wise multifeature structure.
*The geometric summary script assumes that the Null model B embedding has already been generated upstream by FigS6_null_B_featurewise_shuffle.py.
⸻

##Directory structure

Null_model/
├── FigS6_null_A_label_permuted.py
├── FigS6_null_B_featurewise_shuffle.py
├── FigS6_null_B_core_spread_metrics.py
├── README_NullModels_BulkUMAP.md
├── data/
│   ├── 41organs_112525_with_system.csv
│   ├── umap_41organs_cosine_mcs50_withOrgan_with_system.csv
│   └── umap_41organs_cosine_mcs50_nullB_feature_shuffle.csv
├── results/
└── figs/


