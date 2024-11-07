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
import plotly.graph_objs as go
import xarray as xr
import pandas as pd
import numpy as np
import glob
import os


# Initialize lists to accumulate data
all_sp_lats = []
all_sp_lons = []
all_nbrcs = []
all_quality_flags1 = []
all_times = []

# Open the netCDFs in the 'data' directory
data_dir = './data/'
files = glob.glob(os.path.join(data_dir, '20240405*.nc'))
for file in files:
    print(f'Opening {file}')
    ds = xr.open_dataset(file)

    # Grab the meta information
    all_sp_lats.extend(ds['sp_lat'].values.flatten())
    all_sp_lons.extend(ds['sp_lon'].values.flatten())
    all_times.extend(ds['ddm_timestamp_utc'].values.flatten())

    # Grab the data variables
    all_nbrcs.extend(ds['ddm_nbrcs_v1'].values.flatten())
    all_quality_flags1.extend(ds['quality_flags1'].values.flatten())
    
    
# Add the data from the netCDFs to a dataframe to make it easier to filter
data = {
    'Latitude': all_sp_lats,
    'Longitude': all_sp_lons,
    'Quality Flags': all_quality_flags1,
    'NBRCS': all_nbrcs 
}
df = pd.DataFrame(data)

# Remove all rows with a NaN for the NBRCS or the 1st bit of the quality 
# flags is set
df = df.dropna(subset=['NBRCS'])
df = df[df['Quality Flags'] & 1 == 0]


# Plot the refl_peaks and sp positions on a map
fig = go.Figure()
fig.add_trace(go.Scattermapbox())
fig.update_layout(mapbox_style='open-street-map',
        mapbox_center_lon=174.8860,  # Center the map on New Zealand
        mapbox_center_lat=-40.9006,
        mapbox_zoom=4, 
        title='Rongowai NBRCS on 2024-04-05')

fig.add_trace(go.Scattermapbox(
            lon=df['Longitude'],
            lat=df['Latitude'],
            opacity=1,
            marker=dict(
                size=8,
                colorscale='viridis',
                color=df['NBRCS'],
                cmin=-0.15,
                cmax=0.15,
                colorbar=dict(
                    title='NBRCS',
                    titleside='right',
                    len=0.75,
                    y=0.4,  # Set the y position of the colorbar
                    yanchor='middle'
                )
            ),
            name='NBRCS',
            customdata=list(zip(df['Longitude'], df['Latitude'])),
            hovertemplate='NBRCS: %{marker.color:.4f}<br>Latitude: %{customdata[1]:.2f}<br>Longitude: %{customdata[0]:.2f}<extra></extra>', 
            hoverinfo='text', # Show hover text
            showlegend=False
        ))

fig.show()
    
