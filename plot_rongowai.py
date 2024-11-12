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
import glob
import os


# Initialize lists to accumulate data
all_sp_lats = []
all_sp_lons = []
all_snr = []
all_quality_flags1 = []
all_ants = []

# Open the netCDFs in the 'data' directory
data_dir = './data/'
files = glob.glob(os.path.join(data_dir, '*_L1.nc'))
for file in files:
    print(f'Opening {file}')
    ds = xr.open_dataset(file)

    # Grab the meta information
    all_sp_lats.extend(ds['sp_lat'].values.flatten())
    all_sp_lons.extend(ds['sp_lon'].values.flatten())

    # Grab the data variables
    all_snr.extend(ds['ddm_snr'].values.flatten())
    all_ants.extend(ds['ddm_ant'].values.flatten())
    all_quality_flags1.extend(ds['quality_flags1'].values.flatten())
    
    
# Add the data from the netCDFs to a dataframe to make it easier to filter
data = {
    'Latitude': all_sp_lats,
    'Longitude': all_sp_lons,
    'Quality Flags': all_quality_flags1,
    'SNR': all_snr ,
    'Antenna': all_ants
}
df = pd.DataFrame(data)

# Remove all rows with a NaN for the SNR or the 1st bit of the quality 
# flags is set
df = df.dropna(subset=['SNR'])
df = df[df['Quality Flags'] & 1 == 0]

'''
The definition of the antenna column is as follows:

The antenna that received the reflected GPS signal associated with the DDM.
0 = none
1 = zenith (never used)
2 = nadir_LHCP
3 = nadir_RHCP

We want to only keep the data where the antenna is Left Hand Circular Polarized
(LHCP) co-polarization data.
'''
df = df[df['Antenna'] == 2]


# Plot the refl_peaks and sp positions on a map
fig = go.Figure()
fig.update_layout(mapbox_style='open-street-map',
        mapbox_center_lon=174.8860,  # Center the map on New Zealand
        mapbox_center_lat=-40.9006,
        mapbox_zoom=4, 
        title='Rongowai SNR on 2024-04-04 UTC')

fig.add_trace(go.Scattermapbox(
            lon=df['Longitude'],
            lat=df['Latitude'],
            opacity=1,
            marker=dict(
                size=8,
                colorscale='viridis',
                color=df['SNR'],
                cmin=0.0,
                cmax=10.0,
                colorbar=dict(
                    title='Digital Delay Doppler Map (DDM) SNR)',
                    titleside='right',
                    len=0.75,
                    y=0.4,  # Set the y position of the colorbar
                    yanchor='middle'
                )
            ),
            name='SNR',
            customdata=list(zip(df['Longitude'], df['Latitude'])),
            hovertemplate='SNR: %{marker.color:.4f} <br>Latitude: %{customdata[1]:.2f}<br>Longitude: %{customdata[0]:.2f}<extra></extra>', 
            hoverinfo='text', # Show hover text
            showlegend=False
        ))

fig.show()
    
