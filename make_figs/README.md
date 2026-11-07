# Figure-generating scripts for Wind-driven Antarctic Circumpolar Current-subpolar gyre interactions and their impact on poleward heat transport pathways, JGR: Oceans

Analysis and figure code for the MITgcm idealized Southern Ocean experiments in
Coffey et al., JGR: Oceans, 2026. Scripts read raw MITgcm output and produce
the paper's figures. Figure titles often won't match as they were assembled in Figma.

## Contents

| Script | Produces (paper figure) |
|---|---|
| `Fig_1.ipynb` | Fig 1 (wind stress anomaly + bathymetry/fronts/DOT) |
| `Fig_9_S4.ipynb` | Fig 9 (SOSE difference), Fig S4 (zonal wind stress profiles) |
| `Fig_10.ipynb` | Fig 10 (EKE difference, main perturbation) |
| `Fig_meridional_series.ipynb` | Figs 8, S1, S2, S3 (surface-temp anom, z–y transects, MHT, Hovmöller) |
| `hov_schedule3.py` + `run_hovmoller.slurm` | Fig 7 (main Hovmöller, 2×2) |
| `download_era5_stress.py` | Downloads ERA5 wind stress (input for Fig 1 / S4) |

## Environment

These were run on an HPC cluster with **Python 3.6** and the versions below.
The rasterization calls (`im.collections`) rely on this Matplotlib version and
**will error on Matplotlib ≥ 3.8**.

python   3.6
numpy
scipy    1.4.1
pandas   1.0.3
matplotlib 3.2.1
xarray
xgcm
xmitgcm
MITgcmutils

Core dependencies for reading model output: `xmitgcm`, `xgcm`, `MITgcmutils`, `xarray`.

## Data

Scripts read MITgcm binary output via `xmitgcm.open_mdsdataset` from:

<exp_home_dir>/<experiment_name>/results/   # model output (.data/.meta)
<exp_home_dir>/<experiment_name>/input/params.p   # pickled run config

**You must edit two variables at the top of each script:**

- `group_scratch_dir` — root path to your data
- `exp_names` — list of experiment directory names (with `exp_names_alias` for plot labels)

Two kinds of output are loaded:
- `output` — instantaneous snapshots (`*_inst`, e.g. `THETA_inst`)
- `avgs`   — time-averaged diagnostics (e.g. `UVEL`, `VVELTH`, `UVELSQ`)

Time stamps are reconstructed from filenames and `deltaT` in `params.p`, then
stored in `ds.attrs['time']` (seconds). Years = `ds.attrs['time'] / secsInYears`.

## Running

Notebooks: open and run top-to-bottom after setting the paths above.

Fig 7 (batch):
sbatch run_hovmoller.slurm   # edit module loads / account / email first


## Adapting to your own experiments

- Point `group_scratch_dir` / `exp_names` at your runs.
- Index 0 of `exp_names` is treated as the **control**; perturbation panels are
  plotted as (perturbation − control). Order matters.
- Common knobs near the top of each cell/script:
  - `tidxequil`, `tidx` — time-average window (indices into the averaged output)
  - `y_min_km`, `y_max_km` — meridional crop (Hovmöller)
  - `time_downsample` — temporal coarsening factor (Hovmöller)
  - `dep_lvls` — bathymetry contour levels
  - `clvls` — color levels / ranges
- Grid interpolation uses `xgcm` with a periodic X axis; adjust if your domain
  is not zonally periodic.

## Notes

- Averaging window for time-averaged diagnostics is fixed in the model setup
  (set at run time), not adjustable here.
- MHT decomposition (Fig 8/S2) splits total heat transport into Eulerian MOC,
  gyre/standing-eddy, and transient-eddy components; see the MHT cell comments.
- Figures were selected from parameter sweeps (e.g. a specific year offset or
  y-range). The exact selection used in the paper is noted in each script's header.

