import cdsapi
import os

# Set your specific directory path
save_dir = '/Users/nbcoffey/Documents/gyre_project/ERA5'

# Ensure the directory exists
os.makedirs(save_dir, exist_ok=True)

# Initialize the CDS API client
c = cdsapi.Client()

# Generate a list of years from 1979 to 2025
years = [str(year) for year in range(1979, 2026)]
# years = ['2025']
months = [f"{m:02d}" for m in range(1, 13)]

for year in years:
    output_file = os.path.join(save_dir, f'era5_monthly_surface_stress_{year}.nc')
    
    # Skip downloading if the file already exists
    if os.path.exists(output_file):
        print(f"File {output_file} already exists. Skipping...")
        continue
        
    print(f"Requesting monthly data for {year}...")
    
    try:
        c.retrieve(
            'reanalysis-era5-single-levels-monthly-means',
            {
                'format': 'netcdf',
                'product_type': 'monthly_averaged_reanalysis',
                'variable': [
                    'eastward_turbulent_surface_stress',
                    'northward_turbulent_surface_stress',
                ],
                'year': year,
                'month': months,
                'time': '00:00', # Required format for monthly means
                # 'area': [-50, -180, -90, 180], # Uncomment this if you ONLY want the Southern Ocean to save space
            },
            output_file
        )
        print(f"Successfully saved {year} data to {output_file}")
    except Exception as e:
        print(f"An error occurred while downloading {year}: {e}")
