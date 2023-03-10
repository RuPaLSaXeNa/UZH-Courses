import numpy as np
import pandas as pd
import geopandas as gpd
from bokeh.io import save, output_file
from datetime import datetime, timedelta
from bokeh.palettes import Spectral6

from bokeh.layouts import gridplot
from bokeh.io import show
import bokeh.palettes as bp
from bokeh.plotting import figure, curdoc
from bokeh.transform import linear_cmap
from bokeh.layouts import column, row
from bokeh.models import (HoverTool, ColorBar,
                          GeoJSONDataSource,
                          Patches,
                          DateSlider,
                          Button)

# ---------------------------
# Task 1.1: Basic processing

# Hint: feel free to download data from other time from the data link provided above.
yellowTaxiData = pd.read_csv('yellow_tripdata_2021-01.csv')
# yellowTaxiData.head(5)

# Extract datetime and drop unnecessary columns

# Convert columns 'tpep_pickup_datetime' and 'tpep_dropoff_datetime' to datetime object
yellowTaxiData['tpep_pickup_datetime'] = yellowTaxiData['tpep_pickup_datetime'].apply(lambda x: datetime.fromisoformat(str(x)))
yellowTaxiData['tpep_dropoff_datetime'] = yellowTaxiData['tpep_dropoff_datetime'].apply(lambda x: datetime.fromisoformat(str(x)))

# Extract date from the datetime object and add it as new columns named 'pickup_datetime' and 'dropoff_datetime'
yellowTaxiData['pickup_datetime'] = yellowTaxiData['tpep_pickup_datetime'].apply(lambda x: x.date())
yellowTaxiData['dropoff_datetime'] = yellowTaxiData['tpep_dropoff_datetime'].apply(lambda x: x.date())

# Convert the two new datetime columns to string
yellowTaxiData['pickup_datetime'] = yellowTaxiData['pickup_datetime'].apply(lambda x: str(x))
yellowTaxiData['dropoff_datetime'] = yellowTaxiData['dropoff_datetime'].apply(lambda x: str(x))

# drop unnnecessary columns
yellowTaxiData = yellowTaxiData.drop(['RatecodeID', 'trip_distance', 'store_and_fwd_flag', 'payment_type', 'fare_amount',
                                      'extra', 'mta_tax', 'tip_amount', 'tolls_amount', 'improvement_surcharge', 'congestion_surcharge', 'total_amount'], 1)

# Drop outliers
yellowTaxiData.dropna(inplace=True)

discard = ["2009", "2008", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020","2021-02-01", "2021-02-22", "2020-12-31"]

yellowTaxiData = yellowTaxiData[~yellowTaxiData.pickup_datetime.str.contains('|'.join(discard))]
yellowTaxiData = yellowTaxiData[~yellowTaxiData.dropoff_datetime.str.contains('|'.join(discard))]

# ----------------------------------------------------------------------
# Task T1.2: Create two new dataframe for pickup and dropoff seperately

# Create two different dataframes for pickup and dropoff
yellowtaxi_up = yellowTaxiData[['VendorID', 'pickup_datetime', 'passenger_count', 'PULocationID']] # pickup
yellowtaxi_do = yellowTaxiData[['VendorID', 'dropoff_datetime', 'passenger_count', 'DOLocationID']] # dropoff

# Rename the location id in each dataframe
# later you will need it to merge with the shape file, on the colum PULocationID and DOLocationID
yellowtaxi_up.rename(columns={"PULocationID": "LocationID"}, inplace=True)
yellowtaxi_do.rename(columns={"DOLocationID": "LocationID"}, inplace=True)


# Calculate the average number of passengers for each district for pickup and dropoff dataframes
# These two dataframes has #district rows and one column
# This information will be used to encode the color of different district on the map

# Create the pickup dataframe "avg_pass_df_up"
avg_pass_df_up = yellowtaxi_up[["LocationID", "passenger_count"]]
avg_pass_df_up = (avg_pass_df_up.groupby(["LocationID"]).sum()/30).round().astype("int")

# Same for the drop-off dataframe "avg_pass_df_do"
avg_pass_df_do = yellowtaxi_do[["LocationID", "passenger_count"]]
avg_pass_df_do = (avg_pass_df_do.groupby(["LocationID"]).sum()/30).round().astype("int")


# ----------------------------------------------------------------------
# Task T1.3: Create two new dataframes for the number of trips per day for pickup and dropoff.
# The dataframe will contain #district rows and #days columns.
# This dataframe will be needed for the merge step next.

dates = yellowtaxi_up.pickup_datetime.unique().tolist()

numTrips_pickup = pd.DataFrame()

for date in dates:
    temp_df = yellowtaxi_up.loc[yellowtaxi_up["pickup_datetime"] == date]
    temp_df = temp_df[["LocationID", "pickup_datetime"]]
    date_trips = temp_df.groupby(["LocationID"]).count() # count the number of trips after group by LocationID
    numTrips_pickup[date] = date_trips

# Replace all the NaN value with 0
numTrips_pickup = numTrips_pickup.fillna(0).astype("int")

# Do the same thing for drop-off (calculating number of trips)
numTrips_dropoff = pd.DataFrame()

for date in dates:
    temp_df = yellowtaxi_do.loc[yellowtaxi_do["dropoff_datetime"] == date]
    temp_df = temp_df[["LocationID", "dropoff_datetime"]]
    date_trips = temp_df.groupby(["LocationID"]).count() # count the number of trips after group by LocationID
    numTrips_dropoff[date] = date_trips

# Replace all the NaN value with 0
numTrips_dropoff = numTrips_dropoff.fillna(0).astype("int")




# Read shape file using geopandas
shape_raw = gpd.read_file('taxi_zones.shp', encoding='utf-8')

# get latitude and longitude of the center of the districts
shape_raw["latitude"] = shape_raw.geometry.centroid.to_crs(epsg=4326).x
shape_raw["longitude"] = shape_raw.geometry.centroid.to_crs(epsg=4326).y

# convert everything into real coordinates
shape_raw["geometry"] = shape_raw["geometry"].to_crs(epsg=4326)
district_poly = shape_raw.drop(['OBJECTID', 'borough'], 1)
# ------------------------------------------------------------------------------------------
# T1.4 Merge the taxi and shape data, and build a GeoJSONDataSource for pickup data and dropoff data seperately
# merge dataframes numTrips_pickup and avg_pass_df_up with the shapefile district_poly using pandas.merge
temp_merge_up = avg_pass_df_up.merge(numTrips_pickup, left_index=True, right_index=True)
merged_pickup = district_poly.merge(temp_merge_up, left_index=True, right_index=True)

# merge dataframes numTrips_dropoff and avg_pass_df_do with the shapefile district_poly similarly
temp_merge_do = avg_pass_df_do.merge(numTrips_dropoff, left_index=True, right_index=True)
merged_dropoff = district_poly.merge(temp_merge_do, left_index=True, right_index=True)

# normalize the first date's (i.e. 2021-01-01) dropoff data to set size for circles
min_value = merged_dropoff["2021-01-01"].min()
max_value = merged_dropoff["2021-01-01"].max()
normalized_dropoff = (merged_dropoff["2021-01-01"] - min_value)/ (max_value - min_value)
merged_dropoff['size'] = normalized_dropoff*20

# normalize the first date's (i.e. 2021-01-01) pickup data to set size for circles
min_value = merged_pickup["2021-01-01"].min()
max_value = merged_pickup["2021-01-01"].max()
normalized_pickup = (merged_pickup["2021-01-01"] - min_value)/ (max_value - min_value)
merged_pickup['size'] = normalized_pickup*20



####################################################
#                                                  #
#             Task 2: Map Visualization            #
#                                                  #
####################################################


# ------------------------------------------------------------------------------------------------
# Task 2.1: Build the GeoJSONDataSource for plotting, and define linear color mappers for each map

# Build a GeoJSONDataSource from merged pickup and dropoff
geosource_dropoff = GeoJSONDataSource(geojson=merged_dropoff.to_json())
geosource_pickup = GeoJSONDataSource(geojson=merged_pickup.to_json())

# Create Color Mappers for pickup map and dropoff map using linear_cmap with palette "Viridis256"
mappers = {}
mappers['pickup'] = linear_cmap('LocationID', "Viridis256", 0, 1)
mappers['dropoff'] = linear_cmap('LocationID', "Viridis256", 0, 1)
# ------------------------------------------------------------------
# Task 2.2: Map and circle plotting for dropoff data and pickup data
# Plotting Dropoff
p1 = figure(title='NYC Taxi Dropoff',
            plot_height=600,
            plot_width=700,
            toolbar_location='above',
            tools="pan, wheel_zoom, box_zoom, reset")

p1.xgrid.grid_line_color = None
p1.ygrid.grid_line_color = None

# Plot the map using patches, set the fill_color as mappers['dropoff']
# Plot the circles using circle and set the x, y as the latitude and longitude
dropoff = p1.patches('xs','ys', source = geosource_dropoff, fill_color = mappers['dropoff'])
p1.circle(x='latitude', y='longitude', size="size", source=geosource_dropoff)

hover = HoverTool(tooltips=[('Zone', "@zone")], renderers=[dropoff])
p1.add_tools(hover)

# Plotting Pickup
p2 = figure(title='NYC Taxi Pickup',
            plot_height=600,
            plot_width=700,
            toolbar_location='above',
            tools="pan, wheel_zoom, box_zoom, reset")

p2.xgrid.grid_line_color = None
p2.ygrid.grid_line_color = None

# Plot the map using patches, set the fill_color as mappers['pickup']
pickup = p2.patches('xs','ys', source = geosource_pickup, fill_color = mappers['pickup'])

p2.circle(x='latitude', y='longitude',  size="size", source=geosource_pickup)
hover = HoverTool(tooltips=[('Zone', "@zone")], renderers=[pickup])
p2.add_tools(hover)

# Define time slider using DateSlider with the start being the first day and end being the last day
dates = pd.to_datetime(dates)
timeslider = DateSlider(name='Dates', start=datetime(2021, 1, 1), end=datetime(2021, 1, 31), value=datetime(2021, 1, 1), title= "Dates")


####################################################
#                                                  #
#              Task 3: Add Interaction             #
#                                                  #
####################################################
# ------------------------------------------------------------------------------------------------
# Task 3.1: Complete the callback function

# In the callback function, you should update the circle size and then update the geosource
def callback(attr, old, new):
    # Convert timestamp to datetime
    date = datetime.fromtimestamp(new / 1e3)
    i = date.strftime("%Y-%m-%d")
    min_pickup = merged_pickup[i].min()
    max_pickup = merged_pickup[i].max()

    min_dropoff = merged_dropoff[i].min()
    max_dropoff = merged_dropoff[i].max()

    # The circle size should be recomputed based on the current date that is selected
    merged_pickup.size = (merged_pickup[i]-min_pickup)/(max_pickup-min_pickup)*20
    merged_dropoff.size = (merged_dropoff[i]-min_dropoff)/(max_dropoff-min_dropoff)*20
    
    geosource_dropoff.geojson = merged_dropoff.to_json()
    geosource_pickup.geojson = merged_pickup.to_json()

timeslider.on_change('value', callback)

def animate_update_slider():
    # Extract date from slider's current value
    date = timeslider.value
    date_f = datetime.fromtimestamp(date / 1e3)
    day = date_f + timedelta(days=1)
    timeslider.value = day

# Define the callback function of button
# The code is complete
def animate():
    global callback_id
    if button.label == '► Play':
        button.label = '❚❚ Pause'
        callback_id = curdoc().add_periodic_callback(animate_update_slider, 500)
    else:
        button.label = '► Play'
        curdoc().remove_periodic_callback(callback_id)

button = Button(label='► Play', width=80, height=40)
button.on_click(animate)

# Arrange all the components in one view by using column and row layout
layout1 = column(row(p1, p2), row(timeslider, button))
curdoc().add_root(layout1)
