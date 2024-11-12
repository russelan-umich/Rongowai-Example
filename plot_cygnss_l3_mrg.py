'''
An example Python script that will open up and plot CYGNSS L3 Merge netCDF data

CYGNSS L3 MRG data from the PO.DAAC can be found at:
https://podaac.jpl.nasa.gov/dataset/CYGNSS_L3_MRG_V3.2.1
'''
import plotly.graph_objs as go
import xarray as xr
import pandas as pd
import math

# Open the Hurricane Helene netCDF
netcdf_fn = './data/cyg.ddmi.HELENE.al.2024.09.l3.merge-grid-wind.inter-v20241006-230316.a321.d331.nc'
ds = xr.open_dataset(netcdf_fn)

# Grab the data from the netCDF
wind_speeds = ds['wind_speed'].values
lats = ds['lat'].values
lons = ds['lon'].values
best_track_storm_center_lat = ds['best_track_storm_center_lat'].values
best_track_storm_center_lon = ds['best_track_storm_center_lon'].values
time = ds['time'].values


# Print out the shapes of the data
print(f'Wind speeds shape: {wind_speeds.shape}')
print(f'Lats shape: {lats.shape}')
print(f'Lons shape: {lons.shape}')
print(f'Best track storm center lat shape: {best_track_storm_center_lat.shape}')
print(f'Best track storm center lon shape: {best_track_storm_center_lon.shape}')

# Create a 2D grid of latitudes and longitudes that has the same dimensions as 
# the wind speeds
plot_index = 14
lat_plot_wind = []
lon_plot_wind = []
wind_speeds_to_plot = []

for i in range(len(lats)):
    for j in range(len(lons)):

        # Only grab grid cells within 15 degrees of the storm center
        threshold_deg = 15
        if lats[i] < best_track_storm_center_lat[plot_index] - threshold_deg or\
                lats[i] > best_track_storm_center_lat[plot_index] + threshold_deg:
            continue
        if lons[j] < best_track_storm_center_lon[plot_index] - threshold_deg or \
                lons[j] > best_track_storm_center_lon[plot_index] + threshold_deg:
            continue

        # Ignore grid cells with NaN values
        if math.isnan(wind_speeds[plot_index, i, j]):
            continue

        lat_plot_wind.append(lats[i])
        lon_plot_wind.append(lons[j])
        wind_speeds_to_plot.append(wind_speeds[plot_index, i, j])

# Convert to a datetime object to make printting easier
time_to_plot = pd.to_datetime(str(time[plot_index])) # convert to datetime

# Create the figure
fig = go.Figure()
fig.update_layout(
            mapbox_style='open-street-map',
            mapbox_center_lat=best_track_storm_center_lat[plot_index], 
            mapbox_center_lon=best_track_storm_center_lon[plot_index],
            mapbox_zoom=4, 
            title={'text': f'Hurricane Helene Wind Speeds | {time_to_plot.strftime("%Y-%m-%d")} '\
                        f'| {time_to_plot.strftime("%H:%M:%S")} UTC', 
                   'x' : 0.05, 
                   'y' : 0.95, 
                   'xanchor' : 'left', 
                   'yanchor' : 'top'
            }
        )

fig.add_trace(go.Scattermapbox(
            lon=lon_plot_wind,
            lat=lat_plot_wind,
            opacity=1,
            marker=dict(
                size=8,
                colorscale='jet',
                color=wind_speeds_to_plot,
                cmin=0,
                cmax=25,
                colorbar=dict(
                    title='Wind Speed (m/s)',
                    titleside='right',
                    len=0.75,
                    y=0.4,  # Set the y position of the colorbar
                    yanchor='middle'
                )
            ),
            name='Wind Speed',
            showlegend=False
        ))

fig.show()