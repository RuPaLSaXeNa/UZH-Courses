#!/usr/bin/env python
# coding: utf-8

#Import necessary libraries
import pandas as pd
import numpy as np
from bokeh.io import output_file, show, save,curdoc, output_notebook
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool,FactorRange, NumeralTickFormatter,HBar, DatetimeTickFormatter
from bokeh.models.widgets import Select
from bokeh.layouts import column, row, gridplot
import bokeh.palettes as bp # uncomment it if you need special colors that are pre-defined
import datetime as dt
from math import pi
from bokeh.layouts import gridplot
from bokeh.models import BoxSelectTool, LassoSelectTool

# ----- PART1: SCATTER PLOT ----------

#Data Pre-processing
#Read data
df = pd.read_csv('data.csv')

np.random.seed(10)

#Remove some of the data because there is too much :/ (Do not touch this part.)
remove_n = 1455000
drop_indices = np.random.choice(df.index, remove_n, replace=False)
df = df.drop(drop_indices)

#Drop the rows that has larger trip_duration value than 2000. They are outliers in our case.
df = df[df.trip_duration <= 2000]
#For the scatterplot, in the x-axis we need the dates. So,extract dates from the dataframe, we will use the 'pickup_datetime' column.
#df['pickup_datetime'] = ...
df["date"]  = df.apply(lambda x: x["pickup_datetime"].split()[0], axis=1)
df["date"] = pd.to_datetime(df["date"])

#Color operations
    # Vendor_id will be color coded. Append different color to different vendor_id. 
    # Color column is already created for you and filled with a default color. 

color = list()
for i in range(len(df.index)):
    color.append("#A9A9A9")

df['color'] = color

#Assign colors according to vendor_id
for idx in df.index:
  if df["vendor_id"][idx] == 1:
    df["color"][idx]= "#FF0000"
  elif df["vendor_id"][idx] == 2:
    df["color"][idx] = "#00FF00"

#Replace vendor_id -> 1,2 with "vendor_1","vendor_2"
df['vendor_id'] = df['vendor_id'].replace(1, "vendor_1")
df['vendor_id'] = df['vendor_id'].replace(2, "vendor_2")


#Create your dataframe for the scatterplot, and sort it by the "dates" column
#Hint: What you need for the scatterplot dataframe are "trip_duration", "dates", "vendor_id", "color", and "passenger_count". 
#Extract these necessary information from the main dataframe.

df_scatterplot = df[["trip_duration", "date", "vendor_id", "color", "passenger_count"]]
df_scatterplot = df_scatterplot.sort_values(by="date")


#Convert datetime to string
df_scatterplot['date'] = df_scatterplot['date'].apply(lambda x: x.strftime("%Y-%m-%d"))

#Create the ColumnDataSource by first creating a dictionary
data = {
  "trip_duration": list(df_scatterplot["trip_duration"]),
  "date": list(df_scatterplot["date"]),
  "vendor_id": list(df_scatterplot["vendor_id"]),
  "color": list(df_scatterplot["color"]),
  "passenger_count": list(df_scatterplot["passenger_count"])
}

source_scatter = ColumnDataSource(data)


#Set your x-range
#Hint: Your x-range should contain all of the dates.

x_Range = list(dict.fromkeys(source_scatter.data['date']))


#For interaction we will use "Lasso Selection" and "Box Selection" tools.
TOOLS="lasso_select, box_select, reset"

#Create figure for scatterplot.
p = figure(tools=TOOLS, plot_width=3000, plot_height=900,
           toolbar_location="above",x_range = x_Range,
           title="NYC Taxi Traffic")

p.yaxis.axis_label = "Trip Duration (seconds)"
p.xaxis.axis_label = "Dates"
p.xaxis.major_label_orientation = pi/4
p.xaxis.major_label_text_font_size = '8px'
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
p.sizing_mode = "stretch_both"
p.select(LassoSelectTool).select_every_mousemove = False
p.select(BoxSelectTool).select_every_mousemove = False


#Create hover tool.
#Hover tool must show : Date,Trip duration,number of passengers and vendor_id
hover = HoverTool(tooltips = [
                              ('Date', "@date"),
                              ('Trip_duration', "@trip_duration"),
                              ('Number_of_Passengers', "@passenger_count"),
                              ('Vendor_ID', "@vendor_id"),
])
p.add_tools(hover)

#Create the scatterplot, be aware that the size of the circles should encode the number of passengers.
scatter = p.scatter(x=source_scatter.data["date"],  y=source_scatter.data["trip_duration"], color=source_scatter.data["color"], size=source_scatter.data["passenger_count"])

# ------------ PART2: HISTOGRAM OF TRIP DURATION ----------------

# Create the  histogram
# Reference Links:
    #https://www.tutorialspoint.com/numpy/numpy_histogram_using_matplotlib.htm 
    #https://www.geeksforgeeks.org/numpy-histogram-method-in-python/
    #https://numpy.org/doc/stable/reference/generated/numpy.histogram.html 

# Hint:
# First you need to extract the trip duration data from the dataframe, then compute the histogram for the whole data, with the bins=20
# Second you need to figure out the way to create the histogram only for the selected data,
# And since the selected data are from two vendors, you should plot stacked bar chart for the selected data for two different vendors.
trip_duration = df[["trip_duration"]].to_numpy()
vendor_id = df[["vendor_id"]].to_numpy()

hhist, hedges = np.histogram(trip_duration, bins=20)

hzeros = np.zeros(len(hedges)-1)
hmax = max(hhist)*1.1

LINE_ARGS1 = dict(color="#ffbdbd", line_color=None)
LINE_ARGS2 = dict(color="#d9f5d9", line_color=None)

ph = figure(title="Histogram", tools='', background_fill_color="#fafafa", plot_width=1500, plot_height=200, x_range=p.y_range, y_range=(0, hmax))
ph.xgrid.grid_line_color = None
ph.yaxis.major_label_orientation = np.pi/4

# Use ph.quad() for creating the bins. Please read the reference link carefully. 
# Reference links:
    #https://docs.bokeh.org/en/latest/docs/gallery/histogram.html

ph.quad(top=hhist, bottom=0, left=hedges[:-1], right=hedges[1:], fill_color="white", line_color="navy")

ph.y_range.start = 0
ph.yaxis.axis_label = "Number of Trips"
ph.xaxis.axis_label = "Trip Duration"
# ---------------- PART3: LASSO AND BOX TOOLS SELECTION WIDGET -----------------

# Implement the update function that will be triggered when the lasso or box selection tool is used.
def update(attr, old, new):
  ph.quad(top=hhist, bottom=0, left=hedges[:-1], right=hedges[1:], fill_color="white", line_color="navy")
  nds = new  # index of the data that are selected
  new_trip_duration = trip_duration.copy()
  new_vendor_id = vendor_id.copy()

  # filtering data to selected data using the new index
  new_trip_duration = new_trip_duration[nds]
  new_vendor_id = new_vendor_id[nds]

  # collecting vendor 1 and vendor 2 data seperately
  v1_trip_duration = []
  v2_trip_duration = []

  for i, value in enumerate(new_vendor_id):
    if value[0] == "vendor_2":
      v2_trip_duration.append(new_trip_duration[i][0])
    else:
      v1_trip_duration.append(new_trip_duration[i][0])
  
  # changing data type from list to numpy array
  vendor_1_arr = np.array(v1_trip_duration)
  vendor_2_arr = np.array(v2_trip_duration)

  # updating histogram for vendor 1
  hhist_new_1, hedges_new_1 = np.histogram(vendor_1_arr, bins=20)
  ph.quad(top=hhist_new_1 ,bottom=0, left= hedges[:-1], right=hedges[1:],alpha=0.5,**LINE_ARGS1, fill_color="red")

  # updating histogram for vendor 2
  hhist_new_2, hedges_new_2 = np.histogram(vendor_2_arr, bins=20)
  ph.quad(top=hhist_new_2 +  hhist_new_1,bottom=hhist_new_1, left= hedges[:-1], right=hedges[1:],alpha=0.5,**LINE_ARGS1, fill_color="green")

# Bind the update function to lasso tool and data
scatter.data_source.selected.on_change('indices', update)

# use curdoc to add your widgets to the documents
layout = column(p, row(ph))
curdoc().add_root(layout)