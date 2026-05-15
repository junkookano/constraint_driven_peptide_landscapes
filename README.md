# Constraint-driven peptide sequence landscapes

This repository contains figure-level Python scripts used to generate the main computational figures for the manuscript:

**Compartment-resolved in vivo phage display biopanning reveals constraint-driven peptide sequence landscapes**

## Overview

This repository is a minimal code package for reproducing the main computational figure panels. It contains figure-specific Python scripts, processed input tables, and panel-specific README files.

The repository is limited to main figure code. Exploratory analyses, raw sequencing files, and large intermediate tables are not included.

## Repository structure

```text
Fig1/   Scripts, processed input tables, and README files for Figure 1
Fig2/   Scripts, processed input tables, and README files for Figure 2
Fig3/   Scripts, processed input tables, and README files for Figure 3
Fig4/   Scripts, processed input tables, and README files for Figure 4
```

## Requirements

Install the required Python packages using:

```bash
pip install -r requirements.txt
```

The scripts were developed using Python 3.

## Usage

Run each script from the corresponding figure folder.

Example:

```bash
cd Fig2
python3 Fig2a_rank_curve.py
```

Each script reads processed input files from the local `data/` folder and writes outputs to `figs/` and/or `results/`, as described in the panel-specific README files.

## Data

The `data/` folders contain processed input tables required to reproduce the main figure panels. Raw sequencing data and larger intermediate files are not included in this repository and are described separately in the manuscript Data availability statement.

## License

This repository is released under the MIT License. See `LICENSE.txt` for details.