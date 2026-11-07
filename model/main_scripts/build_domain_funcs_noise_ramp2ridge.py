import numpy as np
import matplotlib.pylab as plt
from opensimplex import OpenSimplex


def add_bathy(run_config, domain_params, grid_params, fz=12, show_plot=True, 
              y_slices_km=[850, 1500], x_slices_km=[], cmap='cividis'):
    
    # TODO: 
    # + add doc string
    # + make variable names more consistent
    
    # zonal grid
    dx = domain_params['Lx']/grid_params['Nx'] # x-grid res
    xx = np.arange(grid_params['Nx'] )*dx
    xx = xx-np.mean(xx) # offset so that x=0 is in the center of the domain

    # meridional grid   
    dy = domain_params['Ly']/grid_params['Ny']   # y-grid res
    yy = np.cumsum(dy*np.ones(grid_params['Ny'] )) - dy/2 
    # Y increases with increasing latitude. Also, following Andrew and offseting Y by dy/2)

    # Plotting mesh
    YY, XX = np.meshgrid(yy, xx)
    
    # create flat-bottomed ocean
    H = domain_params['H']
    h = -H
    
    # add southern shelf
    if domain_params['add_SS']:
        print("Adding southern shelf...")
        h += domain_params['SS_H']*(1-np.tanh((YY-domain_params['SS_slope_Y'])/
                                             domain_params['SS_slope_hW']))/2
            
        
        
    if domain_params['add_DP']:
        print("Adding meridional continent...")
        # create meridional continent that spans the domain
        dd = domain_params['slope_hW']/domain_params['DP_dX'] # ratio of slope length-scale to continental width 
        cc = domain_params['slope_hW']
        X0 = domain_params['DP_X']
        dX = domain_params['DP_dX']
        
        try: 
            MR_HoS = domain_params['MR_HoS']
        except KeyError:
            MR_HoS = 0
        
        if domain_params['DP_continent']:
            H_MR = H+MR_HoS # max height of meridional ridge
        else:
            H_MR = domain_params['MR_H_given_DPnoC'] # max height of meridional ridge
        
        h_MR, MR_x = add_meridional_ridge(XX, YY, X0, dX, cc, H_MR)

        
        #cut out drake passage 
        print("cutting out Drake Passage...")
        Y0 = domain_params['DP_Y_mid']
        dY = domain_params['DP_dY']
        Y01 = domain_params['DP_Y_mid1']
        dY1 = domain_params['DP_dY1']
        H_sill = domain_params['DP_sill_H']
        
        DP_cut = add_zonal_channel(XX, YY, Y01, dY1, cc, H_sill, H_MR, MR_x=MR_x)
        
        # cut out small continent on shelf - NBC edits 2/23/2025
        if domain_params['add_SS']:
            h += DP_cut
            
            if domain_params['DP_continent']:
                h += h_MR                
            else:
                print("No continents...")
                plt.figure(figsize=(10, 5))
                pp = plt.pcolormesh(XX/1e3, YY/1e3, h, shading='auto')#, vmin=h.min(), vmax=0, cmap=cmap)
#                 plt.contour(XX/1e3, YY/1e3, h, [-5], colors='k')
                ax0 = plt.gca()
                plt.ylabel('Y (km)', fontsize=fz)
                plt.xlabel('X (km)', fontsize=fz)
                plt.title('h')

                cb= plt.colorbar(pp)
                cb.set_label('Depth', fontsize=fz)
                
#                 shelf = -H+domain_params['SS_H']*(1-np.tanh((YY-domain_params['SS_slope_Y'])/
#                                              domain_params['SS_slope_hW']))/2
                h2var = -H + DP_cut # no shelf
                mask1 = -np.abs(h) < -np.abs(h2var+h_MR)
                mask2 = -np.abs(h_MR) < 0
                mask = mask1*mask2
                h[mask] = h2var[mask]+h_MR[mask]
#                 h[mask] = - np.abs(h_MR[mask])
               
            
#                 plt.figure(figsize=(10, 5))
#                 pp = plt.pcolormesh(XX/1e3, YY/1e3, DP_cut, vmin=DP_cut.min(), vmax=0, cmap=cmap)
#                 plt.contour(XX/1e3, YY/1e3, DP_cut, [-5], colors='k')
#                 ax0 = plt.gca()
#                 plt.ylabel('Y (km)', fontsize=fz)
#                 plt.xlabel('X (km)', fontsize=fz)
#                 plt.title('DP_cut')

#                 cb= plt.colorbar(pp)
#                 cb.set_label('Depth', fontsize=fz)
                
                plt.figure(figsize=(10, 5))
                pp = plt.pcolormesh(XX/1e3, YY/1e3, mask, shading='auto')#, vmin=DP_cut.min(), vmax=0, cmap=cmap)
#                 plt.contour(XX/1e3, YY/1e3, DP_cut, [-5], colors='k')
                ax0 = plt.gca()
                plt.ylabel('Y (km)', fontsize=fz)
                plt.xlabel('X (km)', fontsize=fz)
                plt.title('mask')

                cb= plt.colorbar(pp)
                cb.set_label('Depth', fontsize=fz)

                plt.figure(figsize=(10, 5))
                pp = plt.pcolormesh(XX/1e3, YY/1e3, h_MR, shading='auto')#, vmin=h_MR.min(), vmax=0, cmap=cmap)
    #             plt.contour(XX/1e3, YY/1e3, h_MR, [-5], colors='k')
                ax0 = plt.gca()
                plt.ylabel('Y (km)', fontsize=fz)
                plt.xlabel('X (km)', fontsize=fz)
                plt.title('h_MR')

                cb= plt.colorbar(pp)
                cb.set_label('Depth', fontsize=fz)
        
            
        else:
            # add to bathymetry
            h += h_MR +DP_cut
        
    
    # curved ridge section
    if domain_params['add_CR']:
        # Define bounding box
    #     x1, x2 = -1500e3, 0#500e3   # Ridge spans from X=-5 to X=5
    #     y1, y2 = 0, Y0   # Ridge spans from Y=-3 to Y=3
        x1 = domain_params['MR_X_min']#domain_params['DP_X']
        x2 = domain_params['X2']
        y1 = domain_params['Y1']
        y2 = domain_params['ZR_Y_mid']

        # Define a polynomial ridge function (e.g., sqrt(X_norm))
        def ridge_function(X_norm):
            return np.power(X_norm, 1/3)#np.sqrt(X_norm)  # Ridge follows y = sqrt(X_norm)

        # Generate the curved ridge
        h_CR = add_curved_ridge(XX, YY, x1, x2, y1, y2, ridge_function, dY, cc, H_CR=domain_params['H_CR'])

        # add MR and Passage quickly
        # Compute perpendicular distance from each grid point to the ridge centerline
        dist_perp = np.abs(XX - x1)

        # Apply tanh() decay function for ridge width
    #     CR_decay = (1 - np.tanh(dist_perp / (4*cc)))
        val = dist_perp / (2*cc) # shortening
        MR_decay = (1 - np.tanh(val - 0.25*np.mean(val)))/2 + (1 - np.tanh(val + 0.25*np.mean(val)))/2
    #     CR_decay = (1 - np.tanh((dist_perp-dY/2)/cc))/2 + (1 + np.tanh((dist_perp+dY/2)/cc))/2 - 1

        # Ridge exists only in [x1, x2] and [y1, y2], set height to zero outside
        h_MR = 1000 * MR_decay * ((XX >= x1) & (XX <= x1+400e3) & (YY >= y2))

        # Plot the ridge
        plt.figure(figsize=(10, 5))
        plt.contourf(XX/1e3, YY/1e3, h_CR, levels=20, cmap="viridis")
        plt.colorbar(label="Ridge Height")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.title("Curved Ridge within Defined Region")
        plt.show()
        h2var = -H + h_CR # flat seafloor with CR
        mask1 = -np.abs(h) < -np.abs(h2var)
        mask2 = -np.abs(h_CR) < 0
        mask = mask1*mask2
        h[mask] = h2var[mask]
        plt.figure(figsize=(10, 5))
        plt.contourf(XX/1e3, YY/1e3, mask)
        plt.colorbar(label="Binary Mask")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.title("Curved Ridge within Mask")
        plt.show()
        
#         h+=h_CR
        
    # ramp to ridge section
    if domain_params['add_R2R']:
        # Define bounding box
    #     x1, x2 = -1500e3, 0#500e3   # Ridge spans from X=-5 to X=5
    #     y1, y2 = 0, Y0   # Ridge spans from Y=-3 to Y=3
        x1 = -2000e3#domain_params['MR_X_min']#domain_params['DP_X']
        x2 = domain_params['X2']
        y1 = domain_params['Y1R2R']
        y2 = domain_params['ZR_Y_mid']
        
        dY = domain_params['DP_dY']
        cc = domain_params['slope_hW']

        # Define a polynomial ridge function (e.g., sqrt(X_norm))
        def rampridge_function(X_norm):
            return np.tanh(X_norm)#np.sqrt(X_norm)  # Ridge follows y = sqrt(X_norm)

        # Generate the curved ridge
        h_CR = add_ramp_to_ridge(XX, YY, x1, x2, y1, y2, rampridge_function, dY, cc, H_CR=domain_params['H_CR'])
        
        #chat
        x_zero_idx = np.argmin(np.abs(xx))  # Closest index to x=0

        # Extract h_CR at x=0 (full y-slice)
        h_CR_at_x0 = h_CR[x_zero_idx, :]  # Shape (Ny,)

        # Create mask for 0 < XX < 500e3
        mask = (XX > 0) & (XX < 500e3)

        # Find x-indices where we need to copy the values
        x_indices_to_fill = np.where((xx > 0) & (xx < 500e3))[0]  # Get valid x indices
        num_x_fill = len(x_indices_to_fill)  # Number of columns to fill

        # Tile correctly along x-dimension
        h_CR[np.ix_(x_indices_to_fill, np.arange(len(yy)))] = np.tile(h_CR_at_x0, (num_x_fill, 1))

        # add MR and Passage quickly
        # Compute perpendicular distance from each grid point to the ridge centerline
#         dist_perp = np.abs(XX - x1)

#         # Apply tanh() decay function for ridge width
#     #     CR_decay = (1 - np.tanh(dist_perp / (4*cc)))
#         val = dist_perp / (2*cc) # shortening
#         MR_decay = (1 - np.tanh(val - 0.25*np.mean(val)))/2 + (1 - np.tanh(val + 0.25*np.mean(val)))/2
#     #     CR_decay = (1 - np.tanh((dist_perp-dY/2)/cc))/2 + (1 + np.tanh((dist_perp+dY/2)/cc))/2 - 1

#         # Ridge exists only in [x1, x2] and [y1, y2], set height to zero outside
#         h_MR = 1000 * MR_decay * ((XX >= x1) & (XX <= x1+400e3) & (YY >= y2))

        # Plot the ridge
        plt.figure(figsize=(10, 5))
        plt.contourf(XX/1e3, YY/1e3, h_CR, levels=20, cmap="viridis")
        plt.colorbar(label="Ridge Height")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.title("Curved Ridge within Defined Region")
        plt.show()
        h2var = -H + h_CR # flat seafloor with CR
        mask1 = -np.abs(h) < -np.abs(h2var)
        mask2 = -np.abs(h_CR) < 0
        mask = mask1*mask2
        h[mask] = h2var[mask]
        plt.figure(figsize=(10, 5))
        plt.contourf(XX/1e3, YY/1e3, mask)
        plt.colorbar(label="Binary Mask")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.title("Curved Ridge within Mask")
        plt.show()
        
        h_modified = h.copy()
#         print(np.shape(h_modified))

        # Indices for x in the range [-1500 km, -1400 km]
        x_mask = (xx >= -2000e3) & (xx <= -1000e3)
        x_inds = np.where(x_mask)[0]

#         print(f"Modifying {len(x_inds)} x-columns between -1500 km and -1400 km...")

        for i in x_inds:
            # Get ridge height (positive) along this x-column
            ridge_col = h_CR[i, :]  # shape (Ny,)

            # Find y index of ridge peak (where ridge is tallest)
            j_peak = np.argmax(ridge_col)
            ridge_height = ridge_col[j_peak]  # e.g., 500

            # Convert to bathymetry value (more negative = deeper)
            target_depth = -H + ridge_height  # e.g., -2500 if ridge_height is 500

            updated_points = 0

            # Traverse southward from ridge peak
            for j in range(j_peak - 1, -1, -1):  # go downward in Y
                if h_modified[i,j] < target_depth:
                    h_modified[i,j] = target_depth
                    updated_points += 1
                else:
                    break  # stop when terrain is shallower than target

#             print(f"X = {xx[i]/1e3:.1f} km | Ridge max at Y = {yy[j_peak]/1e3:.1f} km | "
#                   f"Updated {updated_points} points southward")




        # Plot the result
        plt.figure(figsize=(10, 5))
        plt.pcolormesh(XX / 1e3, YY / 1e3, h_modified, shading='auto', cmap='Blues_r')
        plt.colorbar(label='Modified Bathymetry (m)')
        plt.xlabel("X (km)")
        plt.ylabel("Y (km)")
        plt.title("Southward Ridge Extension Until Higher Topography")
#         plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.show()
        h = h_modified
        
        if domain_params['R2R_piecewiselinear']:
            # === Add NE linear ridge using ramp-to-ridge function ===
            print("Adding linear NE ramp ridge extension...")
            def linear_northeast_ridge(X_norm):
                """Linearly increasing function from X_norm = 0 to 1"""
                return 0.5*X_norm  # simple linear rise from y_start to y_end


            # Define bounding box
            x1_NE = 500e3                      # start at x = 500 km
            y1_NE = y2                         # y_start = where previous ridge ended
            delta_x = 3000e3 #- y1_NE           # rise over this y-range
            x2_NE = x1_NE + delta_x            # end at x = 500 + (2000 - y2)
            y2_NE = linear_northeast_ridge(x2_NE)+y1_NE                     # end at y = 2000 km

            # Create new ridge
            h_NE = add_ramp_to_ridge(XX, YY, x1_NE, x2_NE, y1_NE, y2_NE,
                                     linear_northeast_ridge, dY, cc, H_CR=domain_params['H_CR'])
    #         h_CR = add_ramp_to_ridge(XX, YY, x1, x2, y1, y2, rampridge_function, dY, cc, H_CR=domain_params['H_CR'])
    
            # === Apply Shear Offset if enabled ===
            if domain_params['R2R_shear']:
                print("Applying shear offset normal to ridge...")

                x_shift_center = 1000e3
                offset_km = 150e3

                # Compute unit normal vector to ridge slope
                m = 0.5
                norm_factor = np.sqrt(1 + m**2)
                dx = -m / norm_factor
                dy = 1 / norm_factor

                # Find center y-value at x = x_shift_center
                i_center = np.argmin(np.abs(xx - x_shift_center))
                j_peak = np.argmax(h_NE[i_center, :])
                y_shift_center = yy[j_peak]

                # Build mask: east of fracture line defined normal to ridge
                ridge_shift_mask = XX > (x_shift_center + (YY - y_shift_center) * dx / dy)

                # Compute shift in index space
                dx_shift = dx * offset_km / (xx[1] - xx[0])  # in i
                dy_shift = dy * offset_km / (yy[1] - yy[0])  # in j

                i_coords, j_coords = np.meshgrid(np.arange(h_NE.shape[0]), np.arange(h_NE.shape[1]), indexing='ij')
                i_shifted = i_coords + dx_shift
                j_shifted = j_coords + dy_shift

                coords = np.array([i_shifted, j_shifted])

                from scipy.ndimage import map_coordinates
                h_NE_shifted = h_NE.copy()
                h_NE_shifted[ridge_shift_mask] = map_coordinates(
                    h_NE, coords, order=1, mode='constant')[ridge_shift_mask]
                
                # Plot preview
                plt.figure(figsize=(10, 5))
                plt.pcolormesh(XX / 1e3, YY / 1e3, h_NE_shifted, shading='auto', cmap='viridis')
                plt.colorbar(label="NE Linear Ridge Height (m)")
                plt.title("Shifted")
                plt.xlabel("X (km)")
                plt.ylabel("Y (km)")
                plt.tight_layout()
                plt.show()

                h_NE = h_NE_shifted
                
                if domain_params['R2R_shear_cut']:
                    print("Adding fracture valley into the fracture zone...")

                    # Location of fracture (same as shear center)
                    x_center = 1000e3
                    i_center = np.argmin(np.abs(xx - x_center))
                    j_peak = np.argmax(h_NE[i_center, :])
                    y_center = yy[j_peak]


                    # Fracture zone width and length
                    trench_halfwidth = 75e3  # 150 km total width
                    trench_length = 1500e3   # meters along the line (symmetric)

                    # Compute vector from (x_center, y_center) to every grid point
                    delta_X = XX - x_shift_center
                    delta_Y = YY - y_shift_center

                    # Project onto normal and along-line direction
                    dist_along_line = dx * delta_X + dy * delta_Y
                    dist_along_normal   = dy * delta_X - dx * delta_Y  # axis along the fracture zone

                    # Trench mask: within ±75 km across and ±0.75*length along fracture line
                    trench_mask = (
                        (np.abs(dist_along_normal) < trench_halfwidth) &
                        (np.abs(dist_along_line) < trench_length / 2)
                    )

                    # Apply trench
                    h_NE[trench_mask] = 0.0

                    # Visualize trench mask
                    plt.figure(figsize=(10, 6))
                    plt.pcolormesh(XX / 1e3, YY / 1e3, trench_mask, cmap='Reds', shading='auto')
                    plt.colorbar(label="Fracture Mask")
                    plt.title("Fracture Zone Trench Mask (Correct NW-SE Orientation)")
                    plt.xlabel("X (km)")
                    plt.ylabel("Y (km)")
                    plt.tight_layout()
                    plt.show()






            # Apply only where existing depth is > -2975 m
            h_mask = h < -H+10
            h[ h_mask ] = np.maximum(h[ h_mask ], -H + h_NE[ h_mask ])

            # Plot preview
            plt.figure(figsize=(10, 5))
            plt.pcolormesh(XX / 1e3, YY / 1e3, h_NE, shading='auto', cmap='viridis')
            plt.colorbar(label="NE Linear Ridge Height (m)")
            plt.title("Linear Northeast Ridge Extension")
            plt.xlabel("X (km)")
            plt.ylabel("Y (km)")
            plt.tight_layout()
            plt.show()


        
        if domain_params['add_RP']: # ross plain or step
            # Make a copy of h so we modify safely
            h_modified = h.copy()

            # Define x range over which we apply this
            x_mask = (xx >= -1000e3) & (xx <= 500e3)
            x_inds = np.where(x_mask)[0]

            print(f"Applying 100 m elevation raise between -1000 km and 500 km, south of ridge peaks...")
#             print(-H)
#             print(-H+domain_params['RP_step_H'])

            for i in x_inds:
                # Get column of ramp-to-ridge heights (you can use h_CR if that's the right reference)
                ridge_col = h_CR[i, :]  # shape: (Ny,)

                # Find Y index of ridge peak (most positive height = shallowest)
                j_peak = np.argmax(ridge_col)  # assuming h_CR is positive bump
#                 print(j_peak)

                for j in range(j_peak - 1, -1, -1):  # go *southward* (down in Y)
                    current_depth = h[i, j]
#                     print(current_depth)

                    # Only modify if depth is between -3100 and -2900
                    if -H <= current_depth <= -H+domain_params['RP_step_H']:
                        h_modified[i, j] = max(current_depth, -H+domain_params['RP_step_H'])
#                         print("We're in")
#                     else:
#                         # Stop once we reach shallower than -2900 or deeper than -3100
#                         break

            # Plot result
            plt.figure(figsize=(10, 5))
            plt.pcolormesh(XX / 1e3, YY / 1e3, h_modified, shading='auto', cmap='viridis')
            plt.colorbar(label='Modified Bathymetry (m)')
            plt.xlabel("X (km)")
            plt.ylabel("Y (km)")
            plt.title("Applied +100 m Elevation Band (South of Ridge Peaks)")
            plt.tight_layout()
            plt.show()

            # Final update
            h = h_modified
            
            # adding the linear ramps
            # --- STAGE 1: Ramp in X direction from x = 1000 → 500 km for y ≤ 1000 km
            x_start, x_end = 500e3, 1000e3  # meters
            max_ramp_height = 250           # meters
            # --- Dynamically set y_limit_south by searching from y = 1000 km southward
            x_target = 400e3       # meters
            y_start = 1000e3       # meters
            depth_target = -H+max_ramp_height   # meters
            depth_tol = 0.5        # meters

            # Find x-index closest to 400 km
            i_x = np.argmin(np.abs(xx - x_target))

            # Find y-index closest to y = 1000 km
            j_start = np.argmin(np.abs(yy - y_start))

            # Search southward for first depth ≈ -2750
            j_match = None
            for j in range(j_start, -1, -1):  # go south (decreasing y)
                if abs(h[i_x, j] - depth_target) < depth_tol:
                    j_match = j
                    break

            # Assign y_limit_south
            if j_match is not None:
                y_limit_south = yy[j_match]
                print(f"Updated y_limit_south = {y_limit_south/1e3:.1f} km (where h ≈ {depth_target} m)")
            else:
                y_limit_south = 1000e3  # fallback if not found
                print("No matching depth found south of 1000 km, using default y_limit_south = 1000 km")

#             y_limit_south = 1000e3          # meters

            x_ramp_mask = (XX >= x_start) & (XX <= x_end) & (YY <= y_limit_south)
            x_ramp_fraction = (x_end - XX) / (x_end - x_start)
            x_ramp_fraction = np.clip(x_ramp_fraction, 0, 1)
            x_ramp_values = x_ramp_fraction * max_ramp_height
            h[x_ramp_mask] = np.maximum(h[x_ramp_mask], -H+x_ramp_values[x_ramp_mask])

            # --- STAGE 2: Vertical ramp from y = 1500 → 1000 km
            x_target = 400e3     # meters
            y_target = 1500e3    # meters
            depth_threshold = -2990  # meters

            # Step 1: Find x-index closest to 400 km
            i_x = np.argmin(np.abs(xx - x_target))

            # Step 2: Find y-indices where yy ≥ 1500 km
            y_inds_north = np.where(yy >= y_target)[0]

            # Step 3: Search in that y-range for the first j where h[i_x, j] < -2990
            j_match = None
            for j in y_inds_north:
                if h[i_x, j] < depth_threshold:
                    j_match = j
                    break

            # Step 4: Report or handle if not found
            if j_match is not None:
                print(f"Depth at x = {xx[i_x]/1e3:.1f} km and y = {yy[j_match]/1e3:.1f} km is {h[i_x, j_match]:.2f} m")
            else:
                print(f"No point found at x = 400 km and y ≥ 1500 km with depth < {depth_threshold} m.")
#             y_north = 1500e3
            y_south = y_limit_south #1000e3

            # Find index ranges in the y and x arrays
            j_y1000 = np.argmin(np.abs(yy - y_south))
            j_y1500 = j_match#np.argmin(np.abs(yy - y_north))

            i_xstart = np.searchsorted(xx, x_start)
            i_xend = np.searchsorted(xx, x_end)

            # Extract height already added at y = 1000 km and convert from depth (negative) to elevation (positive)
            target_values = h[i_xstart:i_xend, j_y1000] + domain_params['H']  # <- domain_params['H'] is -h base

            # Loop over y from north (1500 km) to south (1000 km) and ramp upward
            for j in range(j_y1500, j_y1000 - 0, -1):
                frac = (yy[j_y1500] - yy[j]) / (yy[j_y1500] - yy[j_y1000])  # 0 → 1
                h[i_xstart:i_xend, j] += frac * target_values
            
            fig, ax = plt.subplots(figsize=(12, 6))

            # Correctly map bathymetry using XX and YY
            c = ax.pcolormesh(XX / 1e3, YY / 1e3, h, shading='auto', cmap='viridis')
            cbar = fig.colorbar(c, ax=ax, label='Modified Bathymetry (m)')

            # Overlay contour at -2900 m
            contour = ax.contour(XX / 1e3, YY / 1e3, h, levels=[-2900], colors='red', linewidths=2)
            ax.clabel(contour, fmt="%.0f", colors='red')

            # Labels and title
            ax.set_xlabel("X (km)")
            ax.set_ylabel("Y (km)")
            ax.set_title("Bathymetry with -2900 m Contour Overlayed")
            plt.tight_layout()
            plt.show()



    
    if domain_params['add_ZR']:
        print("adding zonal ridge...")
        Y0 = domain_params['ZR_Y_mid']
        dY = domain_params['ZR_dY']
        cc = domain_params['slope_hW']
        ZR_H = domain_params['ZR_H']
        
        X0 = domain_params['ZR_X_min']+domain_params['ZR_dX']/2 
        dX = domain_params['ZR_dX']
        
        h_ZR, ZR_y = add_zonal_ridge(XX, YY, Y0, dY, cc, ZR_H, X0=X0, dX=dX)
        
        if domain_params['ZR_intersect']: # goal: get rid of intersection, ZR wins over MR
            h2var = -H
            if domain_params['add_SS']:
                h2var += domain_params['SS_H']*(1-np.tanh((YY-domain_params['SS_slope_Y'])/
                                             domain_params['SS_slope_hW']))/2
#             if domain_params['add_DP']:
#                 h2var += DP_cut
#                 if domain_params['add_NOISE']:
#                     h2var += delambs
#             elif domain_params['add_NOISE']:
#                 h2var += np.transpose(delambs)
            
            mask1 = -np.abs(h) < -np.abs(h2var+h_ZR) # if the Zonal ridge is higher up
            mask2 = -np.abs(h_ZR) < 0
            mask = mask1*mask2
            
            plt.figure(figsize=(10, 5))
            pp = plt.pcolormesh(XX/1e3, YY/1e3, h, shading='auto')#, vmin=h.min(), vmax=0, cmap=cmap)
#                 plt.contour(XX/1e3, YY/1e3, h, [-5], colors='k')
            ax0 = plt.gca()
            plt.ylabel('Y (km)', fontsize=fz)
            plt.xlabel('X (km)', fontsize=fz)
            plt.title('h')
            cb= plt.colorbar(pp)
            cb.set_label('Depth', fontsize=fz)
            plt.figure(figsize=(10, 5))
            pp = plt.pcolormesh(XX/1e3, YY/1e3, h2var+h_ZR, shading='auto')#, vmin=h.min(), vmax=0, cmap=cmap)
#                 plt.contour(XX/1e3, YY/1e3, h, [-5], colors='k')
            ax0 = plt.gca()
            plt.ylabel('Y (km)', fontsize=fz)
            plt.xlabel('X (km)', fontsize=fz)
            plt.title('h2var+h_ZR')
            cb= plt.colorbar(pp)
            cb.set_label('Depth', fontsize=fz)

            plt.figure(figsize=(10, 5))
            pp = plt.pcolormesh(XX/1e3, YY/1e3, mask, shading='auto')#, vmin=DP_cut.min(), vmax=0, cmap=cmap)
#                 plt.contour(XX/1e3, YY/1e3, DP_cut, [-5], colors='k')
            ax0 = plt.gca()
            plt.ylabel('Y (km)', fontsize=fz)
            plt.xlabel('X (km)', fontsize=fz)
            plt.title('mask')
            cb= plt.colorbar(pp)
            cb.set_label('Depth', fontsize=fz)

            plt.figure(figsize=(10, 5))
            pp = plt.pcolormesh(XX/1e3, YY/1e3, h_MR, shading='auto')#, vmin=h_MR.min(), vmax=0, cmap=cmap)
    #             plt.contour(XX/1e3, YY/1e3, h_MR, [-5], colors='k')
            ax0 = plt.gca()
            plt.ylabel('Y (km)', fontsize=fz)
            plt.xlabel('X (km)', fontsize=fz)
            plt.title('h_MR')
            cb= plt.colorbar(pp)
            cb.set_label('Depth', fontsize=fz)
            
            h[mask] = h2var[mask]+h_ZR[mask]
        else:
            # add to bathymetry
            h += h_ZR
            
            
    if domain_params['add_SAP']:

        # Original ellipse parameters
        x_l, x_r = 1250e3, 2250e3
        y_l, y_r = 500e3, domain_params['ZR_Y_mid']
        x_center, y_center = (x_r + x_l) / 2, (y_r + y_l) / 2
        a = (x_r - x_l) / 2  # semi-major axis
        b = (y_r - y_l) / 2  # semi-minor axis
        depth_change = domain_params['SAP_cos_H']  # depression at center on top of step change
        domain_width = 4000e3  # total periodic domain width
        if domain_params['SAP_step_flag']:
            base = domain_params['SAP_step_H']
        else:
            base = 0
        # Function to add a single ellipse
        def add_ellipse(x_center, y_center, a, b, depth_change, base):
            x_norm = (XX - x_center) / a
            y_norm = (YY - y_center) / b
            r = np.sqrt(x_norm**2 + y_norm**2)
            inside = r <= 1
            bump = np.zeros_like(XX)
            bump[inside] = base + depth_change * 0.5 * (1 + np.cos(np.pi * r[inside]))
            return bump

        # Add main ellipse
        depth_profile = add_ellipse(x_center, y_center, a, b, depth_change, base)

        # Add periodic wrap if ellipse extends beyond right edge
        if x_r > 2000e3:
            depth_profile += add_ellipse(x_center - domain_width, y_center, a, b, depth_change, base)

        # Add periodic wrap if ellipse extends beyond left edge (optional)
        if x_l < -2000e3:
            depth_profile += add_ellipse(x_center + domain_width, y_center, a, b, depth_change, base)

        # Plot
        plt.figure(figsize=(10, 5))
        pp = plt.pcolormesh(XX / 1e3, YY / 1e3, depth_profile, shading='auto')
        plt.ylabel('Y (km)', fontsize=12)
        plt.xlabel('X (km)', fontsize=12)
        plt.title('Periodic Cosine Bowl', fontsize=12)
        cb = plt.colorbar(pp)
        cb.set_label('Depth', fontsize=12)
        plt.tight_layout()
        plt.show()

        
        h -= depth_profile
        
#         # clip the bit we don't like to make it a smoother ramp
#         from matplotlib.path import Path
#         # import numpy as np

#         # Define your polygon (in meters)
#         polygon_vertices = [
#             (100e3, 600e3),
#             (500e3, 600e3),
#             (500e3, 800e3),
#             (100e3, 800e3)
#         ]
#         polygon_path = Path(polygon_vertices)

#         # Create mask of where (XX, YY) points are inside the polygon
#         points = np.vstack((XX.ravel(), YY.ravel())).T
#         inside_mask = polygon_path.contains_points(points).reshape(h.shape)

#         # Make a copy and apply the modification inside the polygon
#         h_clipped = h.copy()
#         h_clipped[inside_mask] = np.maximum(h_clipped[inside_mask], -2750)

#         # import matplotlib.pyplot as plt

#         plt.figure(figsize=(10, 5))
#         plt.pcolormesh(XX / 1e3, YY / 1e3, h_clipped, shading='auto', cmap='Blues_r')
#         plt.plot(*np.array(polygon_vertices).T / 1e3, 'r-', lw=2, label='Polygon')
#         plt.colorbar(label='Clipped Bathymetry (m)')
#         plt.xlabel("X (km)")
#         plt.ylabel("Y (km)")
#         plt.title("Bathy Clipped Inside Polygon (>-2750 m)")
#         plt.legend()
# #         plt.gca().invert_yaxis()
#         plt.tight_layout()
#         plt.show()

        

    if domain_params['add_NOISE']:
        # this whole thing is trying to mimic Styles 2023
        
        print("Adding topographic noise...")
        noise_generator = OpenSimplex(seed=1234)  # Seed the noise generator
        Li = domain_params['NOISE_Li'] # list of length scales - 1E3*np.array([240, 120, 60, 30, 9])
        lambs = np.zeros((len(yy), len(xx))) # lambda vector to infill
#         amps = domain_params['NOISE_amp'] # np.array([8, 4, 2, 1, 0.3])
#         for L in Li:
#             lambs += L * noise_generator.noise2d(x=xx/L, y=yy/L)
            
#             # not sure about this one instead
#             lambs += amps * L * noise_generator.noise2array(x=xx/L, y=yy/L)

        for L in zip(Li):
            print('L='+str(L))
            for j in range(len(yy)-1):
                for i in range(len(xx)-1):
                    lambs[j,i] += L * noise_generator.noise2d(xx[i] / L, yy[j] / L)

        # rescale the noise
        lamb_max = domain_params['NOISE_maxlam']
        delambs = lambs - np.mean(lambs) # demean it too, don't change H with this
        
        delambs = delambs * lamb_max / np.max(np.abs(delambs)) # we are rescaling the largest variation to be lamb_max meters tall.
        
        print("shape of delambs:", np.shape(delambs))
        # add to bathymetry
        if domain_params['add_DP']:
            land_mask = np.zeros_like(h) # initialize land mask
            land_mask[h > -lamb_max] = 1 # h=0 is surface depth. This is my thought at least. Copying from code line below with -100 min. Edited to make sure no islands are formed in the process (if 300 meter peak, add to -200 meter seafloor depth, you get island.)
            ocean_mask = 1 - land_mask
            print("shape of ocean_mask:", np.shape(ocean_mask))
            delambs = ocean_mask * np.transpose(delambs)
            
            # demean and rescale again to be safe - mean was off by 0.9 meters
            delambs = delambs - np.mean(delambs) # demean it too, don't change H with this
        
            delambs = delambs * lamb_max / np.max(np.abs(delambs)) # we are rescaling the largest variation to be lamb_max meters tall. If it doesn't matter, the last terms is 300/300=1 for example.
            
            h += delambs 
            
            print('Check: Mean of (supposedly demeaned) lambda:' + str(np.mean(delambs)))
            print('Check: Max abs of final lambda:' + str(np.max(np.abs(delambs))))
            print('Check: Root mean square:' + str(np.sqrt(np.mean(delambs**2))))
        else:
            h += np.transpose(delambs) 
            print('Check: Mean of (supposedly demeaned) lambda:' + str(np.mean(delambs)))
            print('Check: Max abs of final lambda:' + str(np.max(np.abs(delambs))))
            print('Check: Root mean square:' + str(np.sqrt(np.mean(delambs**2))))
        print("shape of delambs:", np.shape(delambs))
        print("shape of h:", np.shape(h))
        # plot the noise
        plt.figure(figsize=(10, 5))
        if domain_params['add_DP']:
            noise = delambs
        else:
            noise = np.transpose(delambs)
        pp = plt.pcolormesh(XX/1e3, YY/1e3, noise, shading='auto', vmin=noise.min(), vmax=noise.max(), cmap=cmap)
        plt.contour(XX/1e3, YY/1e3, noise, [-5], colors='k')
        ax0 = plt.gca()
        plt.ylabel('Y (km)', fontsize=fz)
        plt.xlabel('X (km)', fontsize=fz)
        plt.title('Noise')
        
        cb= plt.colorbar(pp)
        cb.set_label('Amplitude', fontsize=fz)


            
    if domain_params['add_MR']:
        print("adding coastal seamount/meridional ridge...")
        Y0 = domain_params['MR_Y_mid']
        dY = domain_params['MR_dY']
        cc = domain_params['slope_hW']
        ZR_H = domain_params['MR_H']
        
        X0 = domain_params['MR_X_min']+domain_params['MR_dX']/2 
        dX = domain_params['MR_dX']
        
        h_ZR, ZR_y = add_meridional_ridge(XX, YY, X0, dX, cc, ZR_H, Y0, dY) # XX, YY, X0, dX, cc, H_MR, Y0=np.inf, dY=np.inf):
        
        # add to bathymetry
        h += h_ZR
        
        
        if domain_params['add_SAC']:
            print("adding zonal ridge...")
            for cut_X0 in domain_params['SAC_X0']:
                SA_cut = add_meridional_channel(XX, YY, X0=cut_X0, 
                                                dX=domain_params['SAC_dX'], cc=cc, 
                                                H_sill=domain_params['SAC_sill_H'], 
                                                H=ZR_H, MR_y=ZR_y)
                
                h += SA_cut
                
                
    ## Enforce minimum ocean depth and add walls along northern and southern boundaries
    h[h>-100] = 0 # EW NOTE: Not entirely why this done
    # NBC answers: at least for h>0, your continents are above 0. I doubt that does the model any good. Unsure of removing very shallow layer.
    h[:, 0] = 0 
    h[:, -1] = 0
                
        
    #print(XX.shape)
    if show_plot:
       
         # if domain_params['add_NOISE']:
#             # plot plan view
#             plt.figure(figsize=(10, 5))
#     #         pp = plt.pcolormesh(XX/1e3, YY/1e3, h, vmin=h.min(), vmax=0, cmap=cmap)
#             pp = plt.pcolormesh(XX/1e3, YY/1e3, delambs, vmin=-350, vmax=350, cmap=cmap)
#             plt.contour(XX/1e3, YY/1e3, delambs, [-5], colors='k')
#             ax0 = plt.gca()
#             plt.ylabel('Y (km)', fontsize=fz)
#             plt.xlabel('X (km)', fontsize=fz)
#             plt.title('Topographic Noise')

#             cb= plt.colorbar(pp)
#             cb.set_label('Depth', fontsize=fz)

        # plot plan view
        plt.figure(figsize=(10, 5))
        pp = plt.pcolormesh(XX/1e3, YY/1e3, h, shading='auto', vmin=h.min(), vmax=0, cmap=cmap)
        plt.contour(XX/1e3, YY/1e3, h, [-5], colors='k')
        ax0 = plt.gca()
        plt.ylabel('Y (km)', fontsize=fz)
        plt.xlabel('X (km)', fontsize=fz)
        plt.title('H')
        
        cb= plt.colorbar(pp)
        cb.set_label('Depth', fontsize=fz)
        
        fig, axes = plt.subplots(1, 2, figsize=(12, 6))
        
        # plot meridonal slices
        plt.sca(axes[0])
        
        for x_slice in x_slices_km:
            x_idx = np.argmin(np.abs(xx-x_slice*1e3))
            plt.plot(yy/1e3, h[x_idx, :], '.', label="X=%s km" %(xx[x_idx]/1000))
            ax0.axvline(xx[x_idx]/1000, linestyle='--', color='w')
        
        
        plt.xlabel('Y (km)', fontsize=fz)
        plt.ylabel('H (m)', fontsize=fz)
        plt.title('Meridional slices', fontsize=fz)
        plt.grid(True)
        plt.legend()
        
        # plot zonal slices
        plt.sca(axes[1])
        
        for y_slice in y_slices_km:
            y_idx = np.argmin(np.abs(yy-y_slice*1e3))
            plt.plot(xx/1e3, h[:, y_idx], '.', label="Y=%s km" %(yy[y_idx]/1000))
            ax0.axhline(yy[y_idx]/1000, linestyle='--', color='w')
        
        plt.xlabel('X (km)', fontsize=fz)
        plt.ylabel('H (m)', fontsize=fz)
        plt.title('Zonal slices', fontsize=fz)
        plt.ylim(h.min()-100, h.max()+100)
#         plt.ylim(-1600, -1400)
        plt.grid(True)
        plt.legend()

        
        plt.subplots_adjust(wspace=0.3)
        
    return h



def add_curved_ridge(XX, YY, x1, x2, y1, y2, ridge_func, dY, cc, H_CR):
    """
    Function to create a curved ridge where the ridge crest follows a polynomial function
    and the height decays away from this crest using tanh(), within a specified bounding box.

    Parameters:
    -----------
    XX, YY : 2D numpy arrays
        Meshgrid defining the domain coordinates.

    x1, x2 : float
        Bounding box in X-direction (X=0 at x1, X=1 at x2 after normalization).

    y1, y2 : float
        Bounding box in Y-direction where ridge exists.

    ridge_func : function
        Function defining the central ridge path, e.g., lambda X: X**(1/2).

    d_perp : float
        Width of the ridge (perpendicular to the central path).

    cc : float
        Steepness of the ridge decay.

    H_CR : float
        Maximum height of the ridge.

    Returns:
    --------
    h_CR : 2D numpy array
        Ridge height values.
    """

    # Normalize X to [0,1] within [x1, x2]
    X_norm = (XX - x1) / (x2 - x1)
    
    # Ensure values outside [0,1] are ignored
    X_norm = np.clip(X_norm, 0, 1)

    # Compute ridge centerline in physical coordinates
    ridge_y = ridge_func(X_norm) * (y2 - y1) + y1  # Scale back to [y1, y2] range

    # Compute perpendicular distance from each grid point to the ridge centerline
    dist_perp = np.abs(YY - ridge_y)

    # Apply tanh() decay function for ridge width
#     CR_decay = (1 - np.tanh(dist_perp / (4*cc)))
    val = dist_perp / (2*cc) # shortening
    CR_decay = (1 - np.tanh(val - 0.25*np.mean(val)))/2 + (1 - np.tanh(val + 0.25*np.mean(val)))/2
#     CR_decay = (1 - np.tanh((dist_perp-dY/2)/cc))/2 + (1 + np.tanh((dist_perp+dY/2)/cc))/2 - 1

    # Ridge exists only in [x1, x2] and [y1, y2], set height to zero outside
    h_CR = H_CR * CR_decay * ((XX >= x1) & (XX <= x2))#& (YY >= y1) & (YY <= y2))

    return h_CR


def add_ramp_to_ridge(XX, YY, x1, x2, y1, y2, rampridge_function, dY, cc, H_CR):
    """
    Function to create a ramp through ridge ridge where the whole thing follows a tanh function
    and the height decays away from this crest using tanh(), within a specified bounding box.

    Parameters:
    -----------
    XX, YY : 2D numpy arrays
        Meshgrid defining the domain coordinates.

    x1, x2 : float
        Bounding box in X-direction (X=0 at x1, X=1 at x2 after normalization).

    y1, y2 : float
        Bounding box in Y-direction where ridge exists.

    rampridge_func : function
        Function defining the central ridge path, e.g., lambda X: X**(1/2).

    d_perp : float
        Width of the ridge (perpendicular to the central path).

    cc : float
        Steepness of the ridge decay.

    H_R2R : float
        Maximum height of the ridge.

    Returns:
    --------
    h_R2R : 2D numpy array
        Ridge height values.
    """

    # Normalize X to [-1,1] within [x1, x2]
    X_norm = (((XX - x1) / (x2 - x1)) - 0.5)*2
    
    # Ensure values outside [-1,1] are ignored
    X_norm = np.clip(X_norm, -1, 1)

    # Compute ridge centerline in physical coordinates
    ridge_y = rampridge_function(2*X_norm)/rampridge_function(2) * (y2 - y1)/2 + (y1+y2)/2  # Scale back to [y1, y2] range

    # Compute perpendicular distance from each grid point to the ridge centerline
    dist_perp = np.abs(YY - ridge_y)

    # Apply tanh() decay function for ridge width
#     CR_decay = (1 - np.tanh(dist_perp / (4*cc)))
    val = dist_perp / (2*cc) # shortening
    CR_decay = (1 - np.tanh(val - 0.25*np.mean(val)))/2 + (1 - np.tanh(val + 0.25*np.mean(val)))/2
#     CR_decay = (1 - np.tanh((dist_perp-dY/2)/cc))/2 + (1 + np.tanh((dist_perp+dY/2)/cc))/2 - 1

    # Ridge exists only in [x1, x2] and [y1, y2], set height to zero outside
    h_CR = H_CR * CR_decay * ((XX >= x1) & (XX <= x2))#& (YY >= y1) & (YY <= y2))

    return h_CR


def add_meridional_ridge(XX, YY, X0, dX, cc, H_MR, Y0=np.inf, dY=np.inf):
    
    """
    function creates an elongated ridge, centered at X0, with longitudinal extent of dX and max height of H_MR.
    The steepness of the slopes (in the x-direction) is controlled by cc. The latitudinal extent is infinite 
    by default, but can be constrained by Y0 and dY.
   
    """
    
    dd = cc/dX
    # dd: measures the prominence of the plateau. If the plateau is narrow, use a gaussian function.
    # otherwise, use tanh function. This is necessary since the tanh functions (as implemented here) can 
    # grossly underestimate the height of narrow features
    
    if dd>0.2:
        print("using gaussian funcs...")
        # create ridge using gaussian function spanning the length of the domain
        MR_x = np.exp(-(XX-X0)**2/(0.5*dX**2)) 
        h_MR = H_MR*MR_x
        
    else:
        print("using tanh funcs...")
        # combine two tanh functions to get meridional ridge
        MR_x = (1 - np.tanh((XX-X0-dX/2)/cc))/2 + (1 + np.tanh((XX-X0+dX/2)/cc))/2
        MR_x -= 1 # need to offset by H to get the right height
        h_MR = H_MR*MR_x
        
        
       
    # if ridge is finite, limit meridional extent
    if YY.min()<Y0<YY.max() and dY<(YY.max()-YY.min()):
        
        # wrap in meridional function 
        dd2 = cc/dY
        
        if dd2>0.2:
            MR_y = np.exp(-(YY-Y0)**2/(0.5*dY**2))
        else:
            MR_y = (1 - np.tanh((YY-Y0-dY/2)/cc))/2 + (1 + np.tanh((YY-Y0+dY/2)/cc))/2-1
            
        h_MR = MR_y*h_MR
        
    return h_MR, MR_x
             
            
def add_zonal_ridge(XX, YY, Y0, dY, cc, H_ZR, X0=np.inf, dX=np.inf):   
    
    #print(H)

    h_ZR, ZR_y = add_meridional_ridge(YY, XX, Y0=X0, dY=dX, cc=cc, H_MR=H_ZR, X0=Y0, dX=dY)
            
    return h_ZR, ZR_y   
            
            
def add_zonal_channel(XX, YY, Y0, dY, cc, H_sill, H, MR_x=None):
    
    """
    Function to carve out channel/outlet out of a meridional ridge/continent permit zonal flow. 
    
    XX, YY: arrays defining grid
    Y0: latitudinal center of the channel
    DY: latitudinal width of the channel
    cc: steepness of the channel slopes (half-width)
    H_sill: sill depth of the channel (relative to seafloor)
    H: max seafloor depth
    MR_x: zonal profile of ridge
    
    """
    
    dd = cc/dY
    # dd: measures the meridional extent of the sill. If the sill is narrow, the cut is implemented
    # using a gaussian function. Otherwise, a set of tanh functions is used.
    
    #print(dd)
#     print("H: %s" %H)
#     print("H_sill: %s" %H_sill)
    
    if dd>0.2:
        print("using gaussian funcs...")
        # create ridge using gaussian function spanning the length of the domain
        h_cut = (H_sill-H)*np.exp(-(YY-Y0)**2/(0.5*dY**2)) 
        
    else:
        print("using tanh funcs...")
        # cut out channel using combination of tanh functions
        cut1 = (H-H_sill)*(1 + np.tanh((YY-Y0-dY/2)/cc))/2
        cut2 = (H-H_sill)*(1 - np.tanh((YY-Y0+dY/2)/cc))/2
        h_cut = cut1+cut2+H_sill-H # spans full meridional extent

    # limit cut in x-direction by wrapping in function used to define meridional continent
    if MR_x is not None:
        h_cut = MR_x*h_cut

    return h_cut


def add_meridional_channel(XX, YY, X0, dX, cc, H_sill, H, MR_y=None):
    
    """
    Function to carve out channel/outlet out of a meridional ridge/continent permit zonal flow. 
    This is a wrapper for add_zonal_channel()
    
    XX, YY: arrays defining grid
    X0: longitudinal center of the channel
    DX: longitudinal width of the channel
    cc: steepness of the channel slopes (half-width)
    H_sill: sill depth of the channel (relative to seafloor)
    H: max seafloor depth
    MR_y: meridional profile of ridge
    
    """

    # flip coordinates and use function to create zonal ridge
    h_cut = add_zonal_channel(XX=YY, YY=XX, Y0=X0, dY=dX, cc=cc, H_sill=H_sill, H=H, MR_x=MR_y)


    return h_cut
            
            
            
            