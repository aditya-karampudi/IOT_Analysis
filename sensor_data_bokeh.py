import pandas as pd
import calendar
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy import stats
import numpy as np
import _pickle as cPickle
from matplotlib.dates import DateFormatter
import warnings
warnings.filterwarnings("ignore")
from bokeh.layouts import row, column
from bokeh.models import Select, Slider, CategoricalColorMapper, ColumnDataSource, HoverTool
from bokeh.palettes import Spectral6, Spectral5, Spectral11
from bokeh.plotting import curdoc, figure
from bokeh.sampledata.autompg import autompg_clean as df
from bokeh.models.glyphs import MultiLine
from bokeh.palettes import Spectral4

initial_df = pd.read_csv("sensordata.csv") #importing the data

initial_df.head() #checking 5 rows

initial_df.shape #dimensions of data

initial_df.describe()

### Lets remove the id column as it has all unique values and this does not help us in any way

initial_df.id.value_counts().head()

initial_df.drop("id",axis=1,inplace=True)

initial_df.isnull().sum() #looking for any null values

initial_df.dtypes #type of columns

## Lets first change each column to their respective category

initial_df['sensor_id'] = initial_df.sensor_id.astype("category")
initial_df['is_original'] = initial_df.is_original.astype("category")

#cleaning the start and end time
initial_df['start_time'] = initial_df['start_time'].astype("str")
initial_df['start_time'] = initial_df['start_time'].str.replace('T',' ')
initial_df['start_time'] = initial_df['start_time'].str.replace('Z','')

initial_df['end_time'] = initial_df['end_time'].str.replace('T',' ')
initial_df['end_time'] = initial_df['end_time'].str.replace('Z','')

initial_df['start_time'] = initial_df.start_time.str[1:-1]
initial_df['end_time'] = initial_df.end_time.str[1:-1]



### Lets start off by some analysis by creating few features

initial_df['start_time'] = initial_df.start_time.astype("str")
initial_df["value"] = initial_df.value.astype(int)
initial_df["date"] = initial_df.start_time.apply(lambda x : x.split()[0])
initial_df['day'] = initial_df.start_time.apply(lambda x : x.split()[0].split("-")[2])
initial_df["hour"] = initial_df.start_time.apply(lambda x : x.split()[1].split(":")[0])
initial_df["minute"] = initial_df.start_time.apply(lambda x : x.split()[1].split(":")[1])
initial_df["seconds"] = initial_df.start_time.apply(lambda x : x.split()[1].split(":")[2])
initial_df['seconds'] = initial_df['seconds'].str.split('.').str[0]
initial_df['hour_minute_seconds'] = initial_df["hour"] + ":" + initial_df['minute'] + ":" + initial_df['seconds']
initial_df['hour_minute_seconds'] = pd.to_datetime(initial_df['hour_minute_seconds'], format = '%H:%M:%S')


initial_df["weekday"] = initial_df.date.apply(lambda dateString : calendar.day_name[datetime.strptime(dateString,"%Y-%m-%d").weekday()])
initial_df['date'] = pd.to_datetime(initial_df['date'], format='%Y-%m-%d')

initial_df["sensor"] = initial_df.sensor_id.map({3802: "Shower", 3803 : "Temperature in Shower",
                                                 3804 : "Light Levels in Shower", 3805 :"Humidity in Shower",
                                                 3807 : "Bathroom", 3809 : "Toilet Flushed" })

def part_of_day(row):
    if row['hour'] < '12':
        val = 'Morning'
    elif ((row['hour'] > '12') & (row['hour'] < '16')):
        val = 'noon'
    elif ((row['hour'] > '16') & (row['hour'] < '20')):
        val = 'evening'
    else:
        val='night'
    return val



def weekend_or_not(row):
    if (row['day_of_week'] == 5):
        val = '1'
    elif (row['day_of_week'] == 6):
        val = '1'
    else:
        val='0'
    return val

initial_df['day'] = initial_df.day.astype(int)
initial_df['part_of_day'] = initial_df.apply(part_of_day, axis=1)
initial_df['day_of_week'] = initial_df.date.dt.dayofweek
initial_df['weekend_or_not'] = initial_df.apply(weekend_or_not, axis=1)


df = initial_df

def add_zero(row):
    return "{:02d}".format(row)

columns = sorted(df.columns)
discrete = [x for x in columns if df[x].dtype == object]
continuous = [x for x in columns if x not in discrete]

sensor_categories = ['Bathroom', 'Shower', 'Toilet Flushed']
sensor_numerics = ['Temperature in Shower', 'Light Levels in Shower', 'Humidity in Shower']
sensor_columns = ['sensor_categories', "sensor_numerics"]

list_day_column = list(df.day.unique())
sorted_date = sorted(list_day_column, key=int) 


def create_figure():
    df2 = df[df.day == int(date.value)]

    if category.value == "sensor_numerics":
        temp = pd.DataFrame(df2[df2.sensor == "Temperature in Shower"])
        humidity = pd.DataFrame(df2[df2.sensor == "Humidity in Shower"])
        Light = pd.DataFrame(df2[df2.sensor == "Light Levels in Shower"])
        hour = pd.DataFrame(df2.hour_minute_seconds.values)
        
        _tools_to_show = 'box_zoom,pan,save,reset,reset,tap,wheel_zoom' 
        hover = HoverTool(tooltips = [("temperature","@$value"), ("humidity", "@value"),
         ("light_value", "@value"), ("hour","@hour_minute_seconds")], show_arrow=False)

        p = figure(plot_height = 400, plot_width = 600, tools = [_tools_to_show,hover ], x_axis_type = 'datetime')

        for data, name, color in zip([temp, humidity, Light], ["Temperature", "Humidity", "Light_levels"], Spectral4):
            p.line(data['hour_minute_seconds'], data['value'], line_width=3, color=color, legend=name)
            p.circle(data['hour_minute_seconds'], data['value'], fill_color="white")
        p.legend.label_text_font_size = "8pt"
        p.legend.location = "top_left"
    #
    #
    # if category.value == "sensor_categories":

            
    return p


def update(attr, old, new):
    layout.children[1] = create_figure()


date = Slider(title='day', start = sorted_date[0], end = sorted_date[-1], value= 3, step=1)
date.on_change('value', update)
    
category = Select(title = 'Category', value = 'sensor_numerics', options = sensor_columns)
category.on_change('value', update)

x = Select(title='X-Axis', value='hour_minute_seconds', options=columns)
x.on_change('value', update)

y = Select(title='Y-Axis', value='value', options=columns)
y.on_change('value', update)

controls = column([category, date,], width=200)
layout = row(controls, create_figure())

curdoc().add_root(layout)
curdoc().title = "Sensor_data"
