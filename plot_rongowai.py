'''
An example Python script that will open up and plot Rongowai netCDF data

To download Rongowai data from the PO.DAAC you can either visit the PO.DAAC's
site via a web browser at: 
https://podaac.jpl.nasa.gov/dataset/RONGOWAI_L1_SDR_V1.0
or through by using the PO.DAAC's data downloader tool:
https://podaac.github.io/tutorials/quarto_text/DataSubscriberDownloader.html

See these instructions for how to set up the PO.DAAC's data downloader tool:
https://podaac.github.io/tutorials/quarto_text/DataSubscriberDownloader.html

This example will looks at data for 2024-04-04. To download the data for this
date using the PO.DAAC's data downloader tool, you can use the following 
command to download the data into a local directory called 'data':

podaac-data-downloader  -sd 2024-04-04T00:00:00Z  -ed 2024-04-05T00:00:00Z -c RONGOWAI_L1_SDR_V1.0 -d ./data/
'''
import plotly.express as px
import xarray as xr
import pandas as pd
import numpy as np
import glob
import os


# Initialize lists to accumulate data
all_sp_lats = []
all_sp_lons = []
all_refl_peaks = []
all_quality_flags1 = []
all_times = []

# Open the netCDFs in the 'data' directory
data_dir = './data/'
files = glob.glob(os.path.join(data_dir, '20240405*.nc'))
for file in files:
    print(f'Opening {file}')
    ds = xr.open_dataset(file)

    # Grab the specular point position information
    all_sp_lats.extend(ds['sp_lat'].values.flatten())
    all_sp_lons.extend(ds['sp_lon'].values.flatten())

    # Grab the peak surface reflectivity
    all_refl_peaks.extend(np.abs(ds['surface_reflectivity_peak'].values.flatten())) 
    all_quality_flags1.extend(ds['quality_flags1'].values.flatten())
    all_times.extend(ds['ddm_timestamp_utc'].values.flatten())
    
# Add the data from the netCDFs to a dataframe to make it easier to filter
data = {
    'Latitude': all_sp_lats,
    'Longitude': all_sp_lons,
    'Quality Flags': all_quality_flags1,
    'Reflectivity': all_refl_peaks 
}
df = pd.DataFrame(data)

# Remove all rows with a NaN for the reflectivity or the 1st bit of the quality 
# flags is set
df = df.dropna(subset=['Reflectivity'])
df = df[df['Quality Flags'] & 1 == 0]


# Plot the refl_peaks and sp positions on a map
# Create the plot using Plotly Express
# Use a colorbar that goes between 0 and 0.2
fig = px.scatter_geo(
    df,
    lat='Latitude',
    lon='Longitude',
    color='Reflectivity',
    hover_name='Reflectivity',  # Show temperature on hover
    color_continuous_scale='Viridis',  # Color scale for temperatures
    projection="natural earth",
    range_color=[0, 0.15] 
)

# Update layout for better visualization
fig.update_layout(
    title='Rongowai Surface Reflectivity Peaks on 2024-04-04',
    geo=dict(
        landcolor='rgb(217, 217, 217)',
        center=dict(lat=-40.9006, lon=174.8860),  # Center on New Zealand
        projection_scale=9  # Zoom level
    ),
    coloraxis_colorbar=dict(
        title="Surface Reflectivity Peak"
    )
)

# Show the interactive plot
fig.show()


    
