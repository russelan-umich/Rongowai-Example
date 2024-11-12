'''
An example Python script that will open up and plot CYGNSS L3 Merge netCDF data

CYGNSS L3 MRG data from the PO.DAAC can be found at:
https://podaac.jpl.nasa.gov/dataset/CYGNSS_L3_MRG_V3.2.1
'''
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import xarray as xr
import pandas as pd
import math

def create_subplot(fig, lats, lons, wind_speeds, plot_index, subplot_row_index, subplot_col_index):

    # Grab only the data that is within 10 degrees of the storm center that
    # have a valid wind speed
    #
    lat_plot_wind = []
    lon_plot_wind = []
    wind_speeds_to_plot = []
    for i in range(len(lats)):
        for j in range(len(lons)):

            threshold_deg = 10
            if lats[i] < best_track_storm_center_lat[plot_index] - threshold_deg or\
                    lats[i] > best_track_storm_center_lat[plot_index] + threshold_deg:
                continue
            if lons[j] < best_track_storm_center_lon[plot_index] - threshold_deg or \
                    lons[j] > best_track_storm_center_lon[plot_index] + threshold_deg:
                continue
            if math.isnan(wind_speeds[plot_index, i, j]):
                continue

            lat_plot_wind.append(lats[i])
            lon_plot_wind.append(lons[j])
            wind_speeds_to_plot.append(wind_speeds[plot_index, i, j])

    # Take the data and create the scattermapbox that can be added to the figure
    #
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
                yanchor='middle'
            )
        ),
        showlegend=False
    ), row=subplot_row_index, col=subplot_col_index)

# Open the Hurricane Helene netCDF and print out all the sizes
#
netcdf_fn = './data/cyg.ddmi.HELENE.al.2024.09.l3.merge-grid-wind.inter-v20241006-230316.a321.d331.nc'
ds = xr.open_dataset(netcdf_fn)

wind_speeds = ds['wind_speed'].values
lats = ds['lat'].values
lons = ds['lon'].values
best_track_storm_center_lat = ds['best_track_storm_center_lat'].values
best_track_storm_center_lon = ds['best_track_storm_center_lon'].values
time = ds['time'].values

print(f'Time shape: {time.shape}')
print(f'Lats shape: {lats.shape}')
print(f'Lons shape: {lons.shape}')
print(f'Wind speeds shape: {wind_speeds.shape}')
print(f'Best track storm center lat shape: {best_track_storm_center_lat.shape}')
print(f'Best track storm center lon shape: {best_track_storm_center_lon.shape}')



# Create a figure with a 2x2 grid of scattermapboxes that correspond to the 4 
# times closest to Hurricane Helene's landfall
#
start_idx = 11
end_idx = 14

titles = []
for i in range(start_idx, end_idx + 1):
    time_to_plot = pd.to_datetime(str(time[i])) # convert to datetime
    titles.append(f'{time_to_plot.strftime("%Y-%m-%d %H:%M:%S")} UTC')

fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=titles,
    specs = [
        [{"type": "scattermapbox"}, {"type": "scattermapbox"}], 
        [{"type": "scattermapbox"}, {"type": "scattermapbox"}]
        ])



# Center all the plots around the Gulf of Mexico. All four mapboxes will have 
# the same settings
#
center_lat = 25.3
center_lon = 270.6
mapbox_settings = dict(
    style='open-street-map',
    center_lat=center_lat, 
    center_lon=center_lon,
    zoom=4)

fig.update_layout(
    mapbox = mapbox_settings,
    mapbox2 = mapbox_settings,
    mapbox3 = mapbox_settings,
    mapbox4 = mapbox_settings,
    title={'text': f'Hurricane Helene Landfall', 
            'x' : 0.05, 
            'y' : 0.95, 
            'xanchor' : 'left', 
            'yanchor' : 'top'
    }
)

create_subplot(fig, lats, lons, wind_speeds, plot_index=11, subplot_row_index=1, subplot_col_index=1)
create_subplot(fig, lats, lons, wind_speeds, plot_index=12, subplot_row_index=1, subplot_col_index=2)
create_subplot(fig, lats, lons, wind_speeds, plot_index=13, subplot_row_index=2, subplot_col_index=1)
create_subplot(fig, lats, lons, wind_speeds, plot_index=14, subplot_row_index=2, subplot_col_index=2)

fig.show()