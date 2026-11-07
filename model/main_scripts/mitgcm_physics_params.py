import numpy as np


# misc constants
secsInHour = 3600
secsInDay = secsInHour*24
secsInYear = secsInDay*365

mInkm = 1000

def get_params01(run_config, grid_params):
    
    #---physical params---#

    params01 = {} 

    # physical constants
    g = 9.81 # acc. due to gravity (m/s**2)
    Omega = 2*np.pi*366/365/86400 # planetary rotation rate 
    Rp = 6400*mInkm # planetary radius (m)
    lat_min = -70 # latitude at southern boundary (degrees)
    f0 = 2*Omega*np.sin(np.deg2rad(lat_min)) # coriolis param (1/s)
    beta = (2*Omega*np.cos(np.deg2rad(lat_min))/Rp) # beta param


    # momentum scheme
    params01['vectorInvariantMomentum'] = True

    #Note: here and elsewhere, we need to be explicit about floats vs ints. E.g., use 12.0 to represent float and
    # 12 for int

    # viscosity parameters
    params01['viscAr'] = 3e-4 # Vertical viscosity
    params01['viscA4'] = 0.0 # Biharmonic viscosity
    params01['viscAh'] = 12.0 #  Horizontal viscosity 
    params01['viscA4Grid'] = 0.1 # Grid-dependent biharmonic viscosity
    params01['viscAhGrid'] = 0.0 # Grid-dependent viscosity
    params01['viscA4GridMax'] = 0.5 
    params01['viscAhGridMax'] = 1.0
    params01['useAreaViscLength'] = False
    params01['useFullLeith'] = True
    params01['viscC4leith'] = 1.0
    params01['viscC4leithD'] = 1.0
    params01['viscC2leith'] = 0.0
    params01['viscC2leithD'] = 0.0

    # advection and time stepping
    params01['tempAdvScheme'] = 80 # needs to be int
    params01['saltAdvScheme'] = 80 # needs to be int
    params01['tempStepping'] = True
    params01['saltStepping'] = run_config['evolve_salt']
    params01['staggerTimeStep'] = True

    # diffusivity
    params01['diffKrT'] = 5e-6 # Vertical temp diffusion 
    params01['diffK4T'] = 0.0 # Bi-harmonic diffusion
    params01['diffKhT'] = 0.0 # Horizontal temp diffusion

    # equation of state
    params01['eosType'] = 'LINEAR'
    params01['tAlpha'] = 1.5e-4 # Linear thermal expansion coeff 
    params01['sBeta'] = 0.0 # Linear thermal expansion coeff (NOTE: needs to be modified if evolving salt!)

    # boundary conditions
    params01['no_slip_sides'] = False
    params01['no_slip_bottom'] = False
    params01['bottomDragLinear'] = 1.1e-3
    params01['bottomDragQuadratic'] = 0.0

    # physical parameters
    params01['f0'] = f0
    params01['beta'] = beta
    params01['gravity'] = g

    # misc
    params01['quasiHydrostatic'] = False
    params01['fPrime'] = 0.0
    params01['ivdc_kappa'] = 0.0
    params01['implicitDiffusion'] = True
    params01['implicitViscosity'] = True
    params01['exactConserv'] = True
    params01['useCDscheme'] = False
    params01['hFacMin'] = 0.1
    params01['readBinaryPrec'] = 64
    params01['useSingleCpuIO'] = True
    params01['debugLevel'] = 1
    params01['useJamartWetPoints'] = True
    params01['useJamartMomAdv'] = True


    # AS: Don't allow partial cell height to fall below min grid spacing
    params01['hFacMinDr'] = np.min(grid_params['delR'])
    
    return params01

def get_params02_04(run_config, grid_params, pChkptFreq):
    
    # numeric solver parameters 
    params02 = {}
    params02['useSRCGSolver'] = True
    params02['cg2dMaxIters'] = 1000
    params02['cg2dTargetResidual'] = 1e-12

    # time stepping parameters 
    params03 = {}
    # params03['useSRCGSolver'] = True
    # params03['cg2dMaxIters'] = 1000
    # params03['cg2dTargetResidual'] = 1e-12
    params03['alph_AB'] = 1/2
    params03['beta_AB'] = 5/12
    params03['nIter0'] = 0 #<<-something that could be updated
    params03['abEps'] = 0.1

    #if run_config['testing']:

    params03['taveFreq'] = 0.0
    params03['dumpFreq'] = 10.0*secsInYear
    params03['monitorFreq'] = 1.0*secsInYear


    params03['dumpInitAndLast'] = True
    params03['pickupStrictlyMatch'] = False

    if run_config['periodic_forcing']:
        # under-construction. There are few more things we need to do here.
        raise ValueError

    #     params03['periodicExternalForcing'] = periodicExternalForcing
    #     params03['externForcingPeriod'] = externForcingPeriod
    #     params03['externForcingCycle'] = externForcingCycle
    
    
    # gather params for data file 
    params04 = {} #<-- using params04 to be consistent with ordering in Andrew's code
    params04['usingCartesianGrid'] = grid_params['usingCartesianGrid']
    params04['usingSphericalPolarGrid'] = grid_params['usingSphericalPolarGrid']
    params04['delX']  = grid_params['delX']
    params04['delY'] = grid_params['delY']
    params04['delR'] = grid_params['delR']

    return params02, params03, params04

def set_obcs_params(run_config, grid_params):
    
    # NOTE: This is mostly copied verbatim from Andrew Stewart's code. I haven't experiment too much with this.
    
    obcs_params01 = {}

    # Enables an Orlanski radiation condition at the northern boundary
    #useOrlanskiNorth = True #<--prona
    OB_Jnorth = grid_params['Ny']*np.ones((grid_params['Nx'])).astype(int)

    obcs_params01['useOrlanskiNorth'] = True
    obcs_params01['OB_Jnorth'] = OB_Jnorth

    # Enforces mass conservation across the northern boundary by adding a
    # barotropic inflow/outflow
    obcs_params01['useOBCSbalance'] = True
    obcs_params01['OBCS_balanceFacN'] = -1.0
    obcs_params01['OBCS_balanceFacE'] = 0.0
    obcs_params01['OBCS_balanceFacS'] = 0.0
    obcs_params01['OBCS_balanceFacW'] = 0.0
    
    ### Velocity averaging time scale - must be larger than deltaT.
    ### The Orlanski radiation condition computes the characteristic velocity
    ### at the boundary by averaging the spatial derivative normal to the 
    ### boundary divided by the time step over this period.
    ### At the moment we're using the magic engineering factor of 3.
    cvelTimeScale = 3*grid_params['deltaT']
    #Max dimensionless CFL for Adams-Basthforth 2nd-order method
    CMAX = 0.45

    obcs_params02 = {}
    obcs_params02['cvelTimeScale'] = cvelTimeScale
    obcs_params02['CMAX'] = CMAX
    
    return obcs_params01, obcs_params02
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    



