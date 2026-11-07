# Model configuration (MITgcm checkpoint67g)

Idealized channel-model configuration for all simulations in Coffey, Wilson &
Prend (2026).

## Directory layout

    simulations/
      main/       6 full-topography experiments (ridge + noise)
      shelfonly/  5 shelf-only experiments
      spinup/     2 parent spin-up runs (control states the branches start from)
      MITgcm_version.txt
    setup/        domain-setup + branch-creation scripts, and DEFAULTS/ templates
    build_and_run/ darwin_amd64_gfortran_v2 (compiler option file), extend_runs
    main_scripts/ helper modules imported by the setup/branch scripts

Each experiment directory under simulations/ contains:
  code/   compile-time headers (SIZE.h, *_OPTIONS.h, DIAGNOSTICS_SIZE.h, ...)
  input/  run-time config (data, data.*, eedata, params.p) and forcing *.bin
  source_info.txt  (branch provenance: parent run + branch iteration)

Note: the large forcing/bathymetry *.bin files are archived on Zenodo
(zenodo_forcing_binaries.tgz) rather than in Git. They can also be regenerated
by the setup scripts.

## Experiment list

Main (full topography), branched from
spinup/shelf_drake500_ramp2ridge500_nocontinent_noise100_noMR_H3km_v02_noaabw_fixZR_80Nz_rerun:
  - ..._year200_layers                          control
  - ..._incr_wsc_SG_subpolarONLYfixMag_...      northward shift of subpolar wind
  - ..._contract_fixMag_...                     southward contraction
  - ..._25pct_wgb_y1000km_...                   +25% westerly bump, y=1000 km
  - ..._25pct_wgb_y1375km_...                   +25% westerly bump, y=1375 km
  - ..._25pct_wgb_y1750km_...                   +25% westerly bump, y=1750 km

Shelf-only, branched from spinup/shelf_H3km_v02_noaabw:
  - ..._layers_yr250                            control (annual-mean output)
  - ..._layers_yr250_monthly                    control (monthly-mean output)
  - ..._incr_wsc_SG_subpolarONLYfixMag_...      northward shift of subpolar wind
  - ..._contract_fixMag_...                     southward contraction
  - ..._25pct_wgb_y1375km_...                   +25% westerly bump, y=1375 km

The two shelf-only controls are the same simulation written at two output
cadences; the _monthly run differs only in tavg_freq (1/12 yr vs 1 yr) and is
used by Figs_3_6a.

## Reproducing a run

1. Generate a configuration:
   - For the spin-ups, run setup/channel_model_setup_SC_ramp2ridge.py
     (NOTE: for the paper main run, set Lx_km = 4000 and a run_name WITHOUT
     the "_2Lx" suffix; the archived notebook shows a developmental 2Lx 
     variant that is not in the paper).
   - For each perturbation, run the corresponding
     setup/create_new_branch_*.py, which branches from the relevant spin-up,
     writes the perturbed forcing (zonalWindFile.bin / surfQFile.bin), and
     configures diagnostics/layers.

2. Build MITgcm (checkpoint67g) using build_and_run/darwin_amd64_gfortran_v2
   as the genmake2 option file (-mods=../code). The setup script writes a
   build.sh into each experiment's build/ directory.

3. Launch: from the experiment's results/ directory,
   `sh copy_inputs.sh` then `sh run.sh`. Use build_and_run/extend_runs to push
   a run to a later year.

See MITgcm_version.txt for version/commit and grid details.
