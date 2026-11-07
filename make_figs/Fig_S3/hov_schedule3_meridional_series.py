import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import os
import pickle

#import sys
import xgcm
from xmitgcm import open_mdsdataset
import MITgcmutils
import matplotlib.ticker as mticker

group_scratch_dir = '/scratch/groups/earlew/nbcoffey'

exp_home_dir = os.path.join(group_scratch_dir, 'research/modeling/MITgcm/experiments')

exp_names = ['shelf_drake500_ramp2ridge500_nocontinent_noise100_noMR_H3km_v02_noaabw_fixZR_80Nz_rerun_branch01_year200_layers', 
             'shelf_drake500_ramp2ridge500_nocontinent_noise100_noMR_H3km_v02_noaabw_fixZR_80Nz_rerun_branch01_25pct_wgb_y1000km_year200_layers',
             'shelf_drake500_ramp2ridge500_nocontinent_noise100_noMR_H3km_v02_noaabw_fixZR_80Nz_rerun_branch01_25pct_wgb_y1375km_year200_layers',
             'shelf_drake500_ramp2ridge500_nocontinent_noise100_noMR_H3km_v02_noaabw_fixZR_80Nz_rerun_branch01_25pct_wgb_y1750km_year200_layers']

exp_names_alias = ['Control', '$y_c=1000$ km', '$y_c=1375$ km', '$y_c=1750$ km']

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
                    'ETAN', 'UVELSQ', 'VVELSQ', 'WVEL']

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

# SAVE TOGGLE - Set to True when you want to save figures
SAVE_FIGURE = True

# USER-ADJUSTABLE PARAMETERS
y_min_km = 400    # Minimum Y position in km
y_max_km = 1000   # Maximum Y position in km
depth_option = 'surface_only'  # Options: 'surface_only' or 'surface_1km'
time_downsample = 6  # Take every Nth timestep (set to 1 for no downsampling)

# COLORBAR SETTINGS
control_vmin = -0.3   # Control experiment range
control_vmax = 2.9
anomaly_vmin = -0.5  # Anomaly range  
anomaly_vmax = 0.5

# Create output directory (only if saving)
if SAVE_FIGURE:
    output_dir = 'hovmoller_plots'
    os.makedirs(output_dir, exist_ok=True)

# Styling parameters - MUCH larger for publication
fz = 24          # Main font size (was 14)
tick_sz = 20     # Tick label size (was 12)
cbar_label_sz = 22  # Colorbar label size
cbar_tick_sz = 18   # Colorbar tick size
contour_label_sz = 18  # Contour label size

# Convert km to meters for filtering
y_min = y_min_km * 1e3
y_max = y_max_km * 1e3

# Calculate number of experiments for subplot layout
n_exp = len(exp_names)
n_cols = 2
n_rows = int(np.ceil(n_exp / n_cols))

# Also increase figure size
fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 12*n_rows), 
                        constrained_layout=True)

# Ensure axes is always 2D array
if n_exp == 1:
    axes = np.array([[axes]])
elif n_rows == 1:
    axes = axes.reshape(1, -1)

print(f"Y range: {y_min_km} - {y_max_km} km")
print(f"Depth selection: {depth_option}")
print("Using uniform grid - simple averaging for Y direction")
print(f"Anomaly colorbar range: {anomaly_vmin} to {anomaly_vmax} °C")
print("="*60)

# Variable to store reference (control) hovmoller
temp_hovmoller_0 = None

# Process each experiment
for i, exp_name in enumerate(exp_names):
    row = i // n_cols
    col = i % n_cols
    ax = axes[row, col]
    
    ds = output[exp_name]
    
    # Crop data in Y direction
    ds_cropped = ds.where((ds.YC >= y_min) & (ds.YC <= y_max), drop=True)
    
    # Crop data in depth and calculate averages
    if depth_option == 'surface_only':
        # Take only the top layer
        ds_cropped = ds_cropped.isel(Z=0)
        depth_str = "Surface Only"
        # Simple average over Y direction (uniform grid)
        temp_spatial_reduced = ds_cropped['THETA'].mean(dim=['YC'])
        
    elif depth_option == 'surface_1km':
        # Crop in Z: Take from surface down to 1km depth
        ds_cropped = ds_cropped.where(ds_cropped.Z <= 1000, drop=True)
        depth_str = "Surface to 1km"

        # Get the volume weights from the already-cropped dataset
        ds_cropped = ds_cropped.assign_coords({'hFacC': ds.hFacC, 'drF': ds.drF})
        volume_weights = ds_cropped.drF * ds_cropped.hFacC

        # Compute the volume-weighted average in Z direction
        temp_z_avg = (ds_cropped['THETA'] * volume_weights).sum(dim='Z') / volume_weights.sum(dim='Z')

        # Average over Y direction (uniform grid)
        temp_spatial_reduced = temp_z_avg.mean(dim=['YC'])

    # EFFICIENT TEMPORAL AVERAGING - vectorized approach
    if time_downsample > 1:
        original_n_times = len(temp_spatial_reduced.time)
        n_bins = original_n_times // time_downsample

        print(f"Time averaging {original_n_times} -> {n_bins} timesteps")
        print(f"Each new timestep represents average of {time_downsample} original timesteps")

        # Vectorized approach - much faster!
        truncated_length = n_bins * time_downsample
        temp_truncated = temp_spatial_reduced.isel(time=slice(0, truncated_length))
        temp_hovmoller = temp_truncated.coarsen(time=time_downsample, boundary='exact').mean()

        # Handle time attributes
        if 'time' in ds.attrs:
            original_time = ds.attrs['time'][:truncated_length]
            # Reshape and average time values for each bin
            time_reshaped = original_time.reshape(n_bins, time_downsample)
            averaged_time_attr = time_reshaped.mean(axis=1)
        else:
            averaged_time_attr = None
        
        print(f"Completed time averaging: {original_n_times} -> {len(temp_hovmoller.time)} timesteps")
    else:
        temp_hovmoller = temp_spatial_reduced
        averaged_time_attr = None

    # Convert time to years and make it start from 0
    if time_downsample > 1 and averaged_time_attr is not None:
        # Use the averaged time values
        t_years = averaged_time_attr / secsInYears
    else:
        # Use original time coordinates
        t_years = ds.attrs['time'] / secsInYears
    t_years_relative = t_years - t_years[0]
    
    # Store reference for anomaly calculations
    if i == 0:
        temp_hovmoller_0 = temp_hovmoller.copy()
        plot_data = temp_hovmoller
        title = exp_names_alias[i]
        cbar_label = 'Temperature (°C)'

        # Print colorbar range diagnostics for control
        data_min = float(plot_data.min())
        data_max = float(plot_data.max())
        print(f"Experiment {i} ({exp_names_alias[i]}) - CONTROL:")
        print(f"  Data range: {data_min:.3f} to {data_max:.3f} °C")

    else:
        # Calculate anomaly relative to control experiment
        anomaly_data = temp_hovmoller - temp_hovmoller_0
        plot_data = anomaly_data
        title = f'{exp_names_alias[i]} Anomaly'
        cbar_label = 'Temperature Anomaly (°C)'

        # Print colorbar range diagnostics for anomalies
        data_min = float(temp_hovmoller.min())
        data_max = float(temp_hovmoller.max())
        anomaly_min = float(anomaly_data.min())
        anomaly_max = float(anomaly_data.max())
        print(f"Experiment {i} ({exp_names_alias[i]}) - ANOMALY:")
        print(f"  Data range: {data_min:.3f} to {data_max:.3f} °C")
        print(f"  Anomaly range: {anomaly_min:.3f} to {anomaly_max:.3f} °C")
    
    # Convert X coordinates to km for plotting
    x_km = ds_cropped.XC / 1e3
    
    # Create meshgrid for plotting
    X, T = np.meshgrid(x_km, t_years_relative)
    
    # Plot the Hovmoller diagram
    if i == 0:
        # Control experiment: use the new range, every 0.2°C
        levels = np.linspace(control_vmin, control_vmax, 200)  # Smooth colors
        im = ax.contourf(X, T, plot_data, levels=levels, cmap='RdYlBu_r', extend='both')
    else:
        # Use diverging colormap for anomalies with very dense colors
        levels = np.linspace(anomaly_vmin, anomaly_vmax, 200)  # Much denser colors
        im = ax.contourf(X, T, plot_data, levels=levels, cmap='RdBu_r', extend='both')

    # Add labeled contour lines
    if i == 0:
        # Contour lines: 0.5, 1.0, 1.5, 2.0
        contour_levels = np.array([0.5, 1.0, 1.5, 2.0])
        contours = ax.contour(X, T, plot_data, levels=contour_levels, colors='black', alpha=0.6, linewidths=0.8)
        ax.clabel(contours, inline=True, fontsize=contour_label_sz, fmt='%.1f°C')
    else:
        # Anomaly plots: every 0.2°C, dashed for negative, solid for positive

        # Negative contours (dashed): -0.4, -0.2 (increasing order)
        negative_levels = np.array([-0.4, -0.2])
        if len(negative_levels) > 0:
            contours_neg = ax.contour(X, T, plot_data, levels=negative_levels, 
                                     colors='black', alpha=0.6, linewidths=0.8, linestyles='--')
            ax.clabel(contours_neg, inline=True, fontsize=contour_label_sz, fmt='%.1f°C')

        # Positive contours (solid): 0.2, 0.4 (increasing order)
        positive_levels = np.array([0.2, 0.4])
        if len(positive_levels) > 0:
            contours_pos = ax.contour(X, T, plot_data, levels=positive_levels, 
                                     colors='black', alpha=0.6, linewidths=0.8, linestyles='-')
            ax.clabel(contours_pos, inline=True, fontsize=contour_label_sz, fmt='%.1f°C')
    
    # Format subplot
    ax.set_xlabel('X Position (km)', fontsize=fz)
    ax.set_ylabel('Time (Years)', fontsize=fz)
    ax.set_title(title, fontsize=fz)
    ax.tick_params(axis='both', which='major', labelsize=tick_sz)
    ax.grid(True, alpha=0.3)
    
    ax.yaxis.set_major_locator(plt.MultipleLocator(5))
    ax.yaxis.set_minor_locator(plt.MultipleLocator(1))
    
    # Add colorbar for each subplot
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label(cbar_label, fontsize=cbar_label_sz)

    # Set specific ticks for each plot type
    if i == 0:  # Control plot
        cbar_ticks = np.arange(control_vmin, control_vmax, 0.2)  # 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0
        cbar.set_ticks(cbar_ticks)
        cbar.set_ticklabels([f'{tick:.1f}' for tick in cbar_ticks])
    else:  # Anomaly plots
        cbar_ticks = np.arange(anomaly_vmin, anomaly_vmax+0.1, 0.1)  # Every 0.1°C including 0
        cbar.set_ticks(cbar_ticks)
        cbar.set_ticklabels([f'{tick:.1f}' for tick in cbar_ticks])

    cbar.ax.tick_params(labelsize=cbar_tick_sz)

print("="*60)

# Hide empty subplots
for i in range(n_exp, n_rows * n_cols):
    row = i // n_cols
    col = i % n_cols
    axes[row, col].set_visible(False)

# Add overall title
fig.suptitle(f'Temperature Hovmöller Plots - {depth_str}\n'
            f'Y: {y_min_km}-{y_max_km} km', fontsize=fz+4)

# Save figure if toggle is on
if SAVE_FIGURE:
    filename = f'hovmoller_meridional_series_all_experiments_coarsentimesteps_{depth_option}_y{y_min_km}-{y_max_km}km_30years.pdf'
    filepath = os.path.join(output_dir, filename)
    fig.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
    print(f'Saved: {filepath}')

plt.show()

print(f"Processed {n_exp} experiments")
