import numpy as np
import matplotlib.pylab as plt
import xarray as xr
import os
import pickle

#import sys
import xgcm
from xmitgcm import open_mdsdataset
import MITgcmutils
import matplotlib.ticker as mticker

def pretty_label(varname, units=None):
    # map MITgcm variable names -> publication labels
    label_map = {
        'THETA': 'Potential temperature',
        # add more if you want later, e.g.:
        # 'SALT': 'Salinity',
        # 'ETAN': 'Sea-surface height',
    }

    unit_map = {
        'THETA': r'$^\circ$C',   # force degree symbol formatting
    }

    label = label_map.get(varname, varname)
    unit_str = unit_map.get(varname, units)

    if unit_str is None or unit_str == '':
        return label
    return f'{label} ({unit_str})'

group_scratch_dir = '/scratch/groups/earlew/nbcoffey'

exp_home_dir = os.path.join(group_scratch_dir, 'research/modeling/MITgcm/experiments')

# exp_names = ['shelf_drake500_ramp2ridge500_nocontinent_noise100_noMR_H3km_v02_noaabw_fixZR_80Nz_rerun_branch01_year200_layers', 
# #              'shelf_drake500_ramp2ridge500_nocontinent_noise100_noMR_H3km_v02_noaabw_fixZR_80Nz_rerun_branch01_incr_wsc_SG_subpolarONLYfixMag_year200_layers',
# #              'shelf_drake500_ramp2ridge500_nocontinent_noise100_noMR_H3km_v02_noaabw_fixZR_80Nz_rerun_branch01_25pct_wgb_y1375km_year200_layers',
# #              'shelf_drake500_ramp2ridge500_nocontinent_noise100_noMR_H3km_v02_noaabw_fixZR_80Nz_rerun_branch01_contract_fixMag_year200_layers',
#             'shelf_drake500_ramp2ridge500_nocontinent_noise100_noMR_H3km_v02_noaabw_fixZR_80Nz_rerun_branch01_25pct_wgb_y1000km_year200_layers',
#             'shelf_drake500_ramp2ridge500_nocontinent_noise100_noMR_H3km_v02_noaabw_fixZR_80Nz_rerun_branch01_25pct_wgb_y1750km_year200_layers']#,
# #              'shelf_drake500_ramp2ridge500_nocontinent_noise100_noMR_H3km_v02_noaabw_fixZR_80Nz_branch01_contract2_both_year200_layers']

# exp_names_alias = ['Control', 
# #                    '$\\tau_E$ N-shift', 
# #                    '$1.25\,\\tau_W^{\\mathrm{Max}}$', 
# #                    '$\\tau_W$ S-shift']
#                    '$y_c=1000$ km',
#                   '$y_c=1750$ km']
### SHELF ONLY ###
exp_names = ['shelf_H3km_v02_noaabw_branch01_layers_yr250_monthly',
            'shelf_H3km_v02_noaabw_branch01_incr_wsc_SG_subpolarONLYfixMag_year250_layers',
            'shelf_H3km_v02_noaabw_branch01_25pct_wgb_y1375km_year250_layers',
            'shelf_H3km_v02_noaabw_branch01_contract_fixMag_year250_layers']
exp_names_alias = ['Shelf Only',
                  '$\\tau_E$ N-shift', 
                   '$1.25\,\\tau_W^{\\mathrm{Max}}$', 
                   '$\\tau_W$ S-shift']

#exp_names = ['shelf_drake500_ramp2ridge500_nocontinent_noise100_noMR_H3km_v02_noaabw_fixZR_80Nz_branch01_year200_layers', 
#             'shelf_drake500_ramp2ridge500_nocontinent_noise100_noMR_H3km_v02_noaabw_fixZR_80Nz_branch01_incr_wsc_SG_year200_layers',
#             'shelf_drake500_ramp2ridge500_nocontinent_noise100_noMR_H3km_v02_noaabw_fixZR_80Nz_branch01_25pct_wgb_y1250km_year200_layers',
#             'shelf_drake500_ramp2ridge500_nocontinent_noise100_noMR_H3km_v02_noaabw_fixZR_80Nz_branch01_contract2_both_year200_layers']

#exp_names_alias = ['No MR', '$\\tau_E$ N-shift', '$1.25\,\\tau_W^{\\mathrm{Max}}$', '$\\tau_W$ S-shift']

run_config = {}
output = {}
prefix_list = ['THETA_inst', 'VVEL_inst', 'UVEL_inst']#, 'ETAN_inst']
# prefix_list = ['UVEL', 'VVEL', 'WVEL', 'THETA',  'UVELTH', 'VVELTH', 'WVELTH', 
#                     'ETAN', 'UVELSQ', 'VVELSQ', 'WVELSQ', 
#                    'TOTTTEND', 'TFLUX', 'ADVr_TH', 'ADVx_TH', 'ADVy_TH', 
#                    'DFrE_TH', 'DFxE_TH', 'DFyE_TH', 'DFrI_TH', 'oceQsw', 'WTHMASS', 
#                   'LaUH1TH', 'LaVH1TH', 'LaHw1TH','LaHs1TH']#, 'ETAN_inst']
# got an issue with Etan at one of these timesteps. Don't love that.
# Could not find the expected file prefixes ['THETA_inst', 'VVEL_inst', 'UVEL_inst', 'ETAN_inst'] 
# at iternum 4.84303e+06. (Instead found ['UVEL_inst', 'THETA_inst', 'VVEL_inst'])

#iters = [80449, 160898, 241347, 321796, 402245, 482694, 563143, 643592, 724041, 804490, 884939]
iters = 'all'
for i,exp_name in enumerate(exp_names):
    print(i)
    
    results_dir = os.path.join(exp_home_dir, exp_name, 'results')

    # load run_config file (saved at the end of the run_config notebook)
    input_dir = os.path.join(exp_home_dir, exp_name, 'input')
    params_fpath = os.path.join(input_dir, 'params.p')
    with open(params_fpath, 'rb') as f:
        run_config[exp_name] = pickle.load(f)
        
    # load model output as an xarray dataset, which is essentially a netcdf file
    output_ds = open_mdsdataset(data_dir=results_dir, prefix=prefix_list, 
                          geometry='cartesian', iters=iters)
    
    output[exp_name] = output_ds
    
# load output that has been averaged over the entire run.
# it is set in the model setup - the averaging window is 50 years since Earle set it to be that. You can go back in and change this, but I am not sure how to change your averaging window in an ad hoc manner.

run_config_avgs = {}
avgs = {}

prefix_list = ['UVEL', 'VVEL', 'WVEL', 'THETA',  'VVELTH', 'UVELTH', 
                    'ETAN', 'UVELSQ', 'VVELSQ']

# prefix_list = ['UVEL', 'VVEL', 'THETA',  'VVELTH', 'UVELTH']

#iters = [80449, 160898, 241347, 321796, 402245, 482694, 563143, 643592, 724041, 804490, 884939]
iters = 'all'
for i,exp_name in enumerate(exp_names):
    print(f"Processing experiment {i}: {exp_name}")
    
    results_dir = os.path.join(exp_home_dir, exp_name, 'results')

    # load run_config file (saved at the end of the run_config notebook)
    input_dir = os.path.join(exp_home_dir, exp_name, 'input')
    params_fpath = os.path.join(input_dir, 'params.p')
    with open(params_fpath, 'rb') as f:
        run_config_avgs[exp_name] = pickle.load(f)
        
    # load model output as an xarray dataset, which is essentially a netcdf file
    avgs_ds = open_mdsdataset(data_dir=results_dir, prefix=prefix_list, 
                          geometry='cartesian', iters=iters)
    avgs[exp_name] = avgs_ds
    
# create time array using file names

secsInDays = 3600*24
secsInMons = secsInDays*30
secsInYears = secsInDays*365

# time_yrs_dict = {}

for i,exp_name in enumerate(exp_names):
    
    results_dir = os.path.join(exp_home_dir, exp_names[i], 'results')

    
    results_fnames = os.listdir(results_dir)
    theta_inst_fnames = [fname for fname in results_fnames 
                         if (fname.startswith('THETA_inst') and fname.endswith('.data'))]


    # get time stamp info from filenames
    iters = np.array([int(fname.split('.')[1]) for fname in theta_inst_fnames])
    iters.sort()
    #print(iters)

    mitgcm_params = run_config[exp_name]['mitgcm_params']['data']
    deltaT = mitgcm_params[2]['deltaT']
    #print(deltaT)
    time_secs = iters*deltaT

    output[exp_name].attrs['time'] = time_secs
    
    # avg ones now
    
    UVELTH_fnames = [fname for fname in results_fnames 
                         if (fname.startswith('UVELTH.') and fname.endswith('.data'))]


    # get time stamp info from filenames
    iters = np.array([int(fname.split('.')[1]) for fname in UVELTH_fnames])
    iters.sort()
    
    mitgcm_params = run_config_avgs[exp_name]['mitgcm_params']['data']
    deltaT = mitgcm_params[2]['deltaT']
    #print(deltaT)
    time_secs_avgs = iters*deltaT

    avgs[exp_name].attrs['time'] = time_secs_avgs
    
print("Snapshot vars:", time_secs.max()/secsInYears)
print("Time-avg vars:", time_secs_avgs.max()/secsInYears)

from matplotlib import colors as mcolors
import os
import matplotlib.pyplot as plt
import numpy as np
import glob

plt.rcParams['text.usetex'] = False
plt.rcParams['mathtext.fontset'] = 'cm'  # or 'stix'
plt.rcParams['mathtext.default'] = 'regular'

# Assuming 'exp_names', 'avgs', and 'output' are defined in the context before this code
tavgvars = False

vble = 'THETA'
dep_lvls = [500, 750, 1250, 1750, 2250, 2900]

# Set consistent font sizes
SMALL_SIZE = 12    # For minor elements
MEDIUM_SIZE = 14   # For most text elements
LARGE_SIZE = 16    # For axis labels and colorbar labels

# Clean up experiment names for filesystem
def clean_filename(name):
    cleanups = {
        '$\\tau_E$ N-shift': 'tau_E_N-shift',
        '$1.25\\,\\tau_W^{\\mathrm{Max}}$': '1.25_tau_W_Max',
        '$\\tau_W$ S-shift': 'tau_W_S-shift',
        '$y_c=1000$ km': 'yc_1000km',
        '$y_c=1750$ km': 'yc_1750km'
    }
    return cleanups.get(name, name.replace(' ', '_'))

# Calculate dynamic frame count based on 30 years
years = 30
total_outputs = years * 365 // 5  # ~2190
total_frames = total_outputs // 5  # ~438

# Loop through the 3 perturbation experiments (skip index 0 which is control)
for pert_idx in range(1, len(exp_names)):
    pert_alias = exp_names_alias[pert_idx]
    clean_alias = clean_filename(pert_alias)
    
    # Create output directory for this perturbation
    output_dir = os.path.join(os.getcwd(), clean_alias)
    os.makedirs(output_dir, exist_ok=True)
    
    # Find the latest frame that has already been processed
    existing_frames = glob.glob(os.path.join(output_dir, "plot_tidx_*.png"))
    if existing_frames:
        # Extract the indices from filenames
        processed_indices = [int(os.path.basename(f).split("_")[-1].split(".")[0]) for f in existing_frames]
        last_processed = max(processed_indices)
        # Find which t value to start from (divide by 5)
        start_t = (last_processed // 5) + 1
        print(f"Resuming from frame {start_t}/{total_frames} (tidx={start_t*5}) for {pert_alias}")
    else:
        start_t = 0
        print(f"Starting from the beginning for {pert_alias}")

    # Loop over `tidx` from where we left off
    for t in range(start_t, total_frames):
        tidx = t*5
        
        # Check if this frame already exists
        plt_filename = os.path.join(output_dir, f"plot_tidx_{tidx}.png")
        if os.path.exists(plt_filename):
            print(f"Skipping frame {t+1}/{total_frames}: {plt_filename} (already exists)")
            continue
        
        # Apply font sizes globally
        plt.rc('font', size=MEDIUM_SIZE)          # Default text size
        plt.rc('axes', titlesize=MEDIUM_SIZE)     # Title size
        plt.rc('axes', labelsize=LARGE_SIZE)      # x and y labels
        plt.rc('xtick', labelsize=MEDIUM_SIZE)    # x tick labels
        plt.rc('ytick', labelsize=MEDIUM_SIZE)    # y tick labels
        plt.rc('legend', fontsize=MEDIUM_SIZE)    # Legend
        plt.rc('figure', titlesize=LARGE_SIZE)    # Figure title
        
        try:
            fig, axes = plt.subplots(3, 1, figsize=(12, 6 * 3))

            # Create the 3-panel layout: control, perturbation, difference
            plot_indices = [0, pert_idx]  # Control and current perturbation
            
            for i in range(3):
                plt.sca(axes[i])

                if i < 2:  # Control and perturbation plots
                    exp_idx = plot_indices[i]
                    exp_name = exp_names[exp_idx]
                    
                    if tavgvars:
                        ds = avgs[exp_name]
                        vble_map = ds[vble][tidx, 0, :, :]  # 0 index for surface layer 
                        vble_map.attrs = ds[vble].attrs
                    else:
                        ds = output[exp_name]
                        vble_map = ds[vble][tidx, 0, :, :]  # 0 index for surface layer
                        vble_map.attrs = ds[vble].attrs

                    x = ds['XC']/1e3
                    y = ds['YC']/1e3
                    z = ds['Z'].values

                    vble_map = vble_map.where(vble_map!=0)
                    units = vble_map.units
                    cmap = 'seismic'
                    
                    # Store for difference plot
                    if i==0:
                        vble_map0 = vble_map
                    elif i==1:
                        vble_map1 = vble_map
                        
                    # Define your specific asymmetric range
                    vmin = -2
                    vmax = 4
                    
                    # Create levels for contourf - keep resolution but use asymmetric range
                    clvls = np.linspace(vmin, vmax, 31)  # 31 levels for smooth transition
                    
                    # Create a normalization that has a white point at 0
                    norm = mcolors.TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)
                    
                else:  # Difference plot (i==2)
                    # For difference plot
                    cmap = 'seismic'
                    vble_map = vble_map1-vble_map0
                    vmin, vmax = -1, 1
                    clvls = np.linspace(vmin, vmax, 41)  # 41 levels for smooth transition
                    norm = mcolors.TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)

                # Use norm parameter to ensure colormap is centered at 0
                im = plt.contourf(x, y, vble_map, clvls, cmap=cmap, norm=norm, extend='both')

                CS = plt.contour(x, y, ds.Depth, dep_lvls, colors='w')
                plt.clabel(CS, CS.levels.astype(int), inline=True, fontsize=MEDIUM_SIZE)

                plt.ylabel("Meridional Distance y (km)")
                plt.xlabel("Zonal Distance x (km)")
                
                if tavgvars:
                    if i<2:
                        tstmp1 = ds.attrs['time'][tidxequil]/secsInYears
                        tstmp2 = ds.attrs['time'][tidx]/secsInYears
                else:
                    tstmp = ds.attrs['time'][tidx]/secsInYears
                    
                if tavgvars:
                    if i<2:
                        plot_alias = exp_names_alias[plot_indices[i]]
                        plt.title("Potential temperature, z-avg'd over top 1km, timesteps-avg'd $t=%.0f$ to $%.0f$ years (%s)" %(tstmp1-1, tstmp2, plot_alias))
                    else:
                        plt.title("Potential temperature anomaly, z-avg'd over top 1km, timesteps-avg'd $t=%.0f$ to $%.0f$ years" %(tstmp1-1, tstmp2))
                else:
                    if i<2:
                        plot_alias = exp_names_alias[plot_indices[i]]
                        plt.title("Surface potential temperature at $t=%.2f$ years (%s)" %(tstmp, plot_alias))
                    else:
                        plt.title("Surface potential temperature anomaly at $t=%.2f$ years" %(tstmp))
                
                cb = plt.colorbar(im)

                # Set sensible tick intervals
                if i < 2:
                    # For first two plots with range -2 to 4
                    cb.set_ticks(np.arange(-2, 5, 1.0))  # Integer ticks
                    cb.set_label(pretty_label(vble, units), size=LARGE_SIZE)
                else:
                    # For difference plot
                    cb.set_ticks(np.arange(-1, 1.1, 0.5))  # 0.5 interval ticks
                    cb.set_label(r'Potential temperature difference ($^\circ$C)', size=LARGE_SIZE)

                # Increase font size for colorbar tick labels
                cb.ax.tick_params(labelsize=MEDIUM_SIZE)

            # Adjust layout to make room for labels
            plt.tight_layout()
            
            # Save the plot
            plt.savefig(plt_filename, dpi=150)
            print(f"Saved frame {t+1}/{total_frames}: {plt_filename}")
            plt.close(fig)  # Close the figure to free memory
            
        except Exception as e:
            print(f"Error processing frame {t+1}/{total_frames} (tidx={tidx}): {str(e)}")
            plt.close(fig) if 'fig' in locals() else None

print("Processing complete!")
