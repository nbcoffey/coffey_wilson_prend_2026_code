#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().run_line_magic('load_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')


# In[1]:


import os
import numpy as np
import matplotlib.pylab as plt
import time
from datetime import datetime

import sys
import imp
import pickle

sys.path.insert(0,'../main_scripts')
import run_analysis_funcs as raf
import run_config_funcs as rcf

#
#exp_name = 'shelf_demo'
# exp_name = 'shelf_demo_50kmres'
# exp_name = 'shelf_drake_ridge_H3km_v02_noaabw'
# exp_name = 'shelf_drake_ridge_noise_H3km_v02_noaabw'
# exp_name = 'shelf_nodrake_ridge_H3km_v02_noaabw'
# exp_name = 'shelf_nodrake_circumpolarridge_H3km_v02_noaabw'
# exp_name = 'shelf_drake_ridge_H3km_v02_noaabw_branch01_neg25pct_wgb'
# exp_name = 'shelf_drake_ridge_noise_H3km_v02_noaabw_max150msimplex'
# exp_name = 'shelf_drake_ridge_noise_white_blocks_smootherNz_H3km_v02_noaabw'
# exp_name = 'shelf_drake_ridge_noise_H3km_v02_testaabw_branch01_1yearoutputs'
# exp_name = 'shelf_drake_noridge_noise_H3km_v02_noaabw'
# exp_name = 'shelf_drake_ridge_seamountzrt_noise_H3km_v02_noaabw'
# exp_name = 'shelf_drake_noridge_noise_H3km_v02_noaabw_branch01_25pct_wgb_y1500km'
# exp_name = 'shelf_drake_ridge_seamountzrt_noise_H3km_v02_noaabw_branch01_sin2_nospongeforce'
# exp_name = 'shelf_drake_ridge_seamountzrt_noise_H3km_v02_noaabw_branch03_sww15north_pe1no0atSB_nospongeforce'
# exp_name = 'shelf_drake_ridge_nocontinent_H3km_v02_noaabw'
# exp_name = 'shelf_drake_longridge_nocontinent_H3km_v02_noaabw'
# exp_name = 'shelf_drake_longridge_nocontinent_H3km_v02_noaabw_branch01_increasterly'
# exp_name = 'shelf_drake_curvedshortridge_nocontinent_H3km_v02_noaabw'
# exp_name = 'shelf_drake500_curvedshortridge_nocontinent_H3km_v02_noaabw'
# exp_name = 'shelf_drake500_curvedshortridge500_nocontinent_H3km_v02_noaabw'
# exp_name = 'shelf_drake500_ramp2ridge500_nocontinent_H3km_v02_noaabw'
# exp_name = 'shelf_drake_MRgap_nocontinent_H3km_v02_noaabw'
# exp_name = 'shelf_drake500_ramp2ridge500_smallabyssalplain_nocontinent_H3km_v02_noaabw'
# exp_name='shelf_drake1500_ramp2ridge1500_linearramps_nocontinent_H3km_v02_noaabw'
# exp_name = 'shelf_drake500_ramp2ridge500_nocontinent_H3km_v02_noaabw_branch01_decr_wsc_SG_nolayers'
# exp_name = 'shelf_drake500_ramp2ridge500_nocontinent_noise_noMR_H3km_v02_noaabw'
# exp_name = 'shelf_drake500_ramp2ridge500_nocontinent_noise100_noMR_H3km_v02_noaabw'
# exp_name = 'shelf_H3km_v02_noaabw'
# exp_name = 'shelf_drake500_ramp2ridge500_nocontinent_noise100_noMR_H3km_v02_noaabw_branch01_incr_wsc_SG_layers'
# exp_name = 'shelf_H3km_v02_noaabw_branch01_layers'
# exp_name = 'shelf_H3km_v02_noaabw_branch01_25pct_wgb_y1250km_layers'
# exp_name = 'shelf_drake500_ramp2ridge500_nocontinent_noise100_H3km_v02_noaabw'
# exp_name = 'shelf_drake500_ramp2ridge500_nocontinent_noise100_noMR_H3km_v02_noaabw_branch01_year200_layers'
# exp_name = 'shelf_drake500_nocontinent_H3km_v02_noaabw'
# exp_name = 'shelf_drake500_nocontinent_H3km_v02_noaabw_branch01_contract2_both_layers'
# exp_name = 'shelf_drake500_ramp2ridge500_nocontinent_H3km_v02_noaabw_fixZR_80Nz'
# exp_name = 'shelf_drake500_ramp2ridge500_nocontinent_H3km_v02_noaabw_fixZR_80Nz_branch01_25pct_wgb_y1250km_year200_layers'
# exp_name = 'shelf_drake500_ramp2ridge500_nocontinent_H3km_v02_noaabw_fixZR_80Nz_branch01_layers'
# exp_name = 'shelf_drake500_ramp2ridge500_nocontinent_H3km_v02_noaabw_fixZR_80Nz_branch01_contract2_south_layers'
# exp_name = 'shelf_drake500_ramp2ridge500_nocontinent_noise100_H3km_v02_noaabw_branch01_incr_wsc_SG_layers'
# exp_name = 'shelf_drake500_ramp2ridge500_nocontinent_noise100_noMR_H3km_v02_noaabw_fixZR_80Nz'
# exp_name = 'shelf_drake500_ramp2ridge500_nocontinent_noise100_H3km_v02_noaabw_branch01_contract2_both_year250_layers'
# exp_name = 'shelf_drake500_ramp2ridge500_nocontinent_noise100_noMR_H3km_v02_noaabw_fixZR_80Nz_branch01_year200_layers'
# exp_name = 'shelf_drake500_ramp2ridge500_nocontinent_noise100_noMR_H3km_v02_noaabw_fixZR_80Nz_branch01_incr_wsc_SG_year200_layers'
# exp_name = 'shelf_drake500_ramp2ridge500_nocontinent_noise100_noMR_H3km_v02_noaabw_fixZR_80Nz_branch01_25pct_wgb_y1250km_year200_layers'
# exp_name = 'shelf_drake500_ramp2ridge500_nocontinent_noise100_noMR_H3km_v02_noaabw_fixZR_80Nz_branch01_contract2_both_year200_layers'
# exp_name = 'shelf_drake500_ramp2ridge500_nocontinent_noise100_noMR_H3km_v02_noaabw_fixZR_80Nz_branch01_25pct_wgb_y1000km_year200_layers'
# exp_name = 'shelf_drake500_ramp2ridge500_nocontinent_noise100_noMR_H3km_v02_noaabw_fixZR_80Nz_branch01_25pct_wgb_y1500km_year200_layers'
# exp_name = 'shelf_drake500_ramp2ridge500_nocontinent_noise100_noMR_H3km_v02_noaabw_fixZR_80Nz_rerun'
# exp_name = 'shelf_H3km_v02_noaabw_branch01_incr_wsc_SG_subpolarONLYfixMag_year250_layers'
# exp_name = 'shelf_drake500_ramp2ridge500_nocontinent_noise100_noMR_H3km_v02_noaabw_fixZR_80Nz_rerun_branch01_all3_year200_layers'
# exp_name = 'shelf_H3km_v02_noaabw_branch01_25pct_wgb_y1375km_year250_layers'
exp_name = 'shelf_drake500_ramp2ridge500_nocontinent_noise100_noMR_H3km_v02_noaabw_fixZR_80Nz_rerun_branch01_25pct_egb_centered_year200_layers'

# exp_name = 'shelf_drake500_ramp2ridge500_nocontinent_noise100_noMR_H3km_v02_noaabw_fixZR_80Nz_2Lx'


# In[ ]:





# In[ ]:





# In[2]:


SUNet_ID = os.environ['HOME'].split('/')[-1]
# os.environ['GROUP_SCRATCH'] 
scratch_dir = '/scratch/groups/earlew'#os.environ['GROUP_SCRATCH']  #'/oak/stanford/groups/earlew'#
exp_dir = os.path.join(scratch_dir, SUNet_ID, 'research/modeling/MITgcm/experiments/')   

exp_path = os.path.join(exp_dir, exp_name)


# In[3]:


exp_path


# In[ ]:





# In[4]:


# check for last pickup file (the script can only extend from a pickup file)
imp.reload(raf)
imp.reload(rcf)
secsInYr = 3600*24*365
params,_ = raf.get_exp_params_py(exp_path, add_hFac=False)
#lastIter = rcf.getLastPickupIter(params['results_path'])
lastIter = rcf.getLastPickupIter(os.path.join(exp_path, 'results'))
pickupSec = int(lastIter)*params['deltaT']
pickupYear = pickupSec/secsInYr
print(lastIter)
print(pickupSec)
print(pickupYear)


# In[5]:


params['results_path']


# In[6]:


# get list of saved iterations
imp.reload(raf)
iters = rcf.getSavedIters(vname='THETA_inst', results_path = params['results_path'])
iters


# In[ ]:





# In[7]:


# get run times

# get creation time of output files
vble_name = 'THETA_inst'
results_files = os.listdir(params['results_path'])
vble_files = [f for f in results_files if f.startswith(vble_name) and f.endswith('.data')]
vble_files.sort()

# # Niall edits just once
# vble_files = vble_files[1:]

time_stmps = np.array([os.path.getctime(os.path.join(params['results_path'], f)) for f in vble_files])

# offset time stamp
time_stmps = time_stmps-time_stmps[0] # note: os.path.getctime rounds to nearest second

# remove negative wall time values
time_stmps[time_stmps<0] = np.nan

# get model time 
iters = np.array([int(f.split('.')[1]) for f in vble_files])
model_time = iters*params['deltaT']
model_time_yrs = model_time/secsInYr


# In[ ]:





# In[8]:


plt.figure(figsize=(8, 6))
fz = 12
plt.plot(time_stmps/3600, model_time/secsInYr, '-o')
plt.ylabel("model time (years)", fontsize=fz)
plt.xlabel("wall time (hours)", fontsize=fz)
plt.grid(True)

# plt.plot(time_stmps, model_time, '-o')
# plt.ylabel("model time (seconds)", fontsize=fz)
# plt.xlabel("wall time (seconds)", fontsize=fz)
# plt.grid(True)


# In[9]:


time_stmps


# In[ ]:





# In[10]:


# Note: run this out for at least year before trying to extrapolate 

dump_range = 10 # use last few runs to compute efficiency
time_stmps_hrs = time_stmps/3600

dt_wallclock = time_stmps_hrs[-1] - time_stmps_hrs[-dump_range]
dt_model = model_time_yrs[-1] - model_time_yrs[-dump_range]

run_eff_yrs_hr = dt_model/dt_wallclock
print("Model efficiency: %.5f model years per wall clock hours" %run_eff_yrs_hr.mean())


# In[11]:


# alternatively 
wall_mins_per_sim_yr = 60/run_eff_yrs_hr.mean()
print("Model efficiency: %.2f wall clock minutes per model year" %wall_mins_per_sim_yr.mean())


# In[ ]:





# In[12]:


# print current run_mitgcm script
with open(os.path.join(params['results_path'], 'run_mitgcm'), 'r') as f:
          print(f.read())


# In[14]:


imp.reload(rcf)

ncpus = params['grid_params']['nPx']*params['grid_params']['nPy']

endyr = 280 #230

# endyr
rcf.extendRun(exp_path, newEndYr=endyr, overWriteFiles=True, printNewRunScript=True, results_path='', ncpus=ncpus,
              wall_mins_per_sim_yr=wall_mins_per_sim_yr*1.1, max_walltime_hrs=72)

# endyr + 10
# rcf.extendRun(exp_path, newEndYr=endyr+10, overWriteFiles=True, printNewRunScript=True, results_path='', ncpus=ncpus,
#               wall_mins_per_sim_yr=wall_mins_per_sim_yr*1.1, max_walltime_hrs=72)

# set overWriteFiles=True, when you're ready to create new


# In[15]:


exp_path


# In[ ]:





# In[ ]:





# In[ ]:




