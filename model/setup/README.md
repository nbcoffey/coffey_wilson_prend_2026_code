# Model setup and branch-creation scripts

## Contents

- `channel_model_setup_SC_ramp2ridge.{ipynb,py}`
    Builds a simulation from scratch: domain/bathymetry, vertical grid,
    initial hydrography, sponge layer, surface wind/heat forcing, vertical
    diffusivity, diagnostics, and all MITgcm `data.*` / `code/*.h` files.
    Also writes the build and job-submission shell scripts.
    NOTE: the archived notebook shows a test variant with run_name "..._2Lx"
    and Lx_km = 2*4000. For the paper's main spin-up, use Lx_km = 4000 and a
    run_name WITHOUT the "_2Lx" suffix.

- `branch/`
    The branch-creation scripts (one per experiment), as run, in both
    `.ipynb` (with inline diagnostic plots) and `.py` form. Each branches from
    a parent spin-up, writes the perturbed surface forcing
    (zonalWindFile.bin / surfQFile.bin), configures the layers and diagnostics
    packages, and extends the run. These are the authoritative record of how
    each experiment's forcing was produced.

- `DEFAULTS/`
    Baseline `code/` headers and `input/` files copied into every new
    experiment directory by the setup script before customization.

## How a branch works

Each `branch/create_new_branch_*` script:
  1. sets `exp_name_old` (parent spin-up) and `exp_name_new` (this experiment);
  2. calls `rcf.createNewBranch(...)` to copy code/input/build and link the
     pickup files for the chosen branch year;
  3. constructs the surface forcing and writes zonalWindFile.bin / surfQFile.bin;
  4. writes the layers and diagnostics configuration
     (`rcf.write_data`, `createLAYERSSIZEh`, `createDIAGSIZEh`);
  5. calls `rcf.extendRun(...)` to set the end year and write the run script.

## Perturbation types

All experiments share an identical heat flux (q0*sin(2*pi*y/Ly)); they differ
only in the zonal wind stress. Three mechanisms appear across the scripts:

  - Westerly strengthening ("..._25pct_wgb_yXXXXkm"):
      a Gaussian bump added to the easterly/westerly profile,
      `taux += bump`, centered at `mu` (km) with width `sig`, amplitude
      25% of tau_east_max. Experiments differ only in `mu`
      (y1000, y1375, y1750).

  - Westerly southward shift ("..._contract_fixMag"):
      the wind-stress spline knots are shifted south by `shift_n = -100e3`.

  - Easterly northward shift ("..._incr_wsc_SG_subpolarONLYfixMag"):
      the spline knots are shifted north by `shift_n = +75e3`, with the
      perturbation confined to the subpolar gyre.

Controls apply no wind perturbation. Shelf-only experiments use the same
mechanisms; they differ from the main experiments only in the parent spin-up,
the output cadence (`tavg_freq = 1/12` for the "_monthly" control), and the
end year.

## Helper modules (in ../main_scripts/)

- `run_config_funcs.py`   : generates all data/namelist/size/SLURM files;
                            createNewBranch, extendRun, etc.
- `run_analysis_funcs.py` : reads run parameters/forcing (get_exp_params_py).
- `build_domain_funcs_noise_ramp2ridge.py` : constructs bathymetry.
- `mitgcm_physics_params.py` : physical/numerical parameter sets.
