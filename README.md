# Coffey, Wilson & Prend (2026) — Code & Model Configuration

Code and idealized-model configuration supporting Coffey, Wilson & Prend (2026),
submitted to *JGR: Oceans*.

## Repository structure

    .
    ├── model/            MITgcm configuration for all simulations (see model/README.md)
    │   ├── simulations/  Per-experiment code/ + input/ (forcing binaries archived on Zenodo)
    │   ├── setup/        Domain-setup and branch-creation scripts (+ DEFAULTS templates)
    │   ├── build_and_run/ Compiler option file and run-extension script
    │   └── main_scripts/ Helper modules (config generation, domain construction, physics params)
    ├── make_figs/        Notebooks that generate all paper and supplementary figures
    │                     (see make_figs/README.md)
    └── requirements.txt  Python dependencies

## Model

Simulations were performed with MITgcm checkpoint67g
(https://github.com/MITgcm/MITgcm; retrieve via `git checkout checkpoint67g`,
commit 29a542dcabc8c4398769a8f5e8ee2206816c8dd9). The model was run with
configuration headers only (no modified Fortran source). See model/README.md
for build and run instructions, the full experiment list, and notes on
reproducing each simulation.

## Figures

All figures are produced by the notebooks in make_figs/. See
make_figs/README.md for which notebook generates each figure and what
input data it requires.

## Data availability

- Model configuration (this repository): the code/ and input/ text
  configuration for every experiment, the setup/branch-creation scripts, and
  the compiler option file are included here.
- Forcing & bathymetry binaries (*.bin): archived on Zenodo
  (zenodo_forcing_binaries.tgz) owing to size; they are also regenerable from
  the setup scripts in model/setup/.
- Raw model output (model results/): not archived here owing to volume;
  available from the authors upon request.

Archived release: [Zenodo DOI — add after release].

## Software environment

    pip install -r requirements.txt

Key dependencies: numpy, scipy, matplotlib, MITgcmutils, gsw, opensimplex,
xarray, xgcm, xmitgcm.

## Citation

Coffey, N. B., Wilson, [initials], & Prend, [initials] (2026). [Title].
Journal of Geophysical Research: Oceans (submitted).
