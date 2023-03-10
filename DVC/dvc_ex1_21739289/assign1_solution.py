import pandas as pd
from bokeh.io import output_file, save
from bokeh.core.properties import value
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool,FactorRange
import bokeh.palettes as bp # uncomment it if you need special colors that are pre-defined
import calendar

#Read data into a dataframe using pandas
df = pd.read_csv('data.csv')

#Convert "pickup_datetime" attribute in the dataframe to datetime type for further processing
df['pickup_datetime'] = pd.to_datetime(df["pickup_datetime"])

#Split datetime object to months and hours, and do the following conversion for months:
    # 5 -> "May" 
    # 3 -> "March" , and so on.
df['pickup_datetime_month'] = df['pickup_datetime'].dt.month
df['pickup_datetime_month'] = df['pickup_datetime_month'].apply(lambda x: calendar.month_name[int(x)].lower())
df['pickup_datetime_hour'] =  df['pickup_datetime'].dt.hour

#Use months as stack names
stacks = ["january","february","march","april","may","june"]

#Calculate the total number of trips for each month grouped by hour(In other words calculate the stack values).
stack_val_jan = (df.loc[df['pickup_datetime_month'] == stacks[0]]).groupby(['pickup_datetime_hour']).size().reset_index(name='counts')
stack_val_feb = (df.loc[df['pickup_datetime_month'] == stacks[1]]).groupby(['pickup_datetime_hour']).size().reset_index(name='counts')
stack_val_mar =(df.loc[df['pickup_datetime_month'] == stacks[2]]).groupby(['pickup_datetime_hour']).size().reset_index(name='counts')
stack_val_april = (df.loc[df['pickup_datetime_month'] == stacks[3]]).groupby(['pickup_datetime_hour']).size().reset_index(name='counts')
stack_val_may =(df.loc[df['pickup_datetime_month'] == stacks[4]]).groupby(['pickup_datetime_hour']).size().reset_index(name='counts')
stack_val_june =(df.loc[df['pickup_datetime_month'] == stacks[5]]).groupby(['pickup_datetime_hour']).size().reset_index(name='counts')

#Manipulate "pickup_datetime_hour" attribute for visualization purposes.
#Extract unique values for pickup_datetime_hour and create the time intervals(0 -> 0-1 , 23 -> 23-0 and so on) using string manipulation.
hours = df['pickup_datetime_hour'].unique()
hours_str = list(map(lambda x: str(x) + '-' + str(x+1) , sorted(hours)))

#Using the information gathered from the data pre-processing step create the ColumnDataSource for visualization.
data = {'hours': hours_str,
        'january': list(stack_val_jan['counts']),
        'february': list(stack_val_feb['counts']),
        'march': list(stack_val_mar['counts']),
        'april': list(stack_val_april['counts']),
        'may': list(stack_val_may['counts']),
        'june': list(stack_val_june['counts'])}

x = [(hr, st) for hr in hours_str for st in stacks]
counts = sum(zip(list(stack_val_jan['counts']),
                      list(stack_val_feb['counts']),
                           list(stack_val_mar['counts'])
                                ,list(stack_val_april['counts'])
                                      ,list(stack_val_may['counts'])
                                            ,list(stack_val_june['counts']), ())) 
source = ColumnDataSource(data=data)

# Visualize the data using bokeh plot functions
p=figure(x_range=FactorRange(*hours_str), plot_height=800, plot_width=800, title='Number of trips in NYC')
p.yaxis.axis_label = "Number of trips"
p.xaxis.axis_label = "Hours"
p.sizing_mode = "stretch_both"
p.xgrid.grid_line_color = None

# Using vbar_stack to plot the stacked bar chart
colors = ["#c9d9d3", "#718dbf", "#e84d60","#c9a9d3", "#328dbf", "#a84d60"]
p.vbar_stack(stacks, x='hours', width=0.9,color=colors, source=source,legend=[value(x) for x in stacks])

# Add HoverTool. HoverTool should show the name of the month, the hours and the number of trips when the mouse hover on each bar.
hover = HoverTool(tooltips=[
        ('month', '@stacks'),
        ('hour', '@hours'), 
        ('number of trips', '$y'),
    ],)

p.add_tools(hover)

# Save the plot as "dvc_ex1.html" using output_file
output_file(filename="dvc_ex1.html", title="Static HTML file")
save(p)