#!/home/pi/dev/ghouse/.venv/bin/python3

import pandas as pd 
import matplotlib.pyplot as plt
import scienceplots 
plt.style.use(['science', 'no-latex'])
import datetime 
import matplotlib.dates as mdates


# TODO: argument to file? 
FNAME = "/home/pi/dev/ghouse/datacollection/tempdata.csv"

#HEADER:  Time, a, b, c, d, e, f
df = pd.read_csv(FNAME, sep=",", header=0, names=["Time", " a", " b", " c", " d", " e", " f", " "])


""" 
Time, a, b, c, d, e, f, 
2025-04-19 13:20:02.158061,22.437,  21.5,21.062,20.687,21.187, 19.75,
2025-04-19 13:26:18.311167,22.437,  21.5,21.125,20.687, 21.25,19.812,
...
"""
# Remove the last column (empty)
df = df.drop(columns=[" "])
# strip whitespace from column names
df.columns = df.columns.str.strip()
# Convert the time column to datetime
df["Time"] = pd.to_datetime(df["Time"], format="%Y-%m-%d %H:%M:%S.%f")
# If there are None values in the columns, replace with Nan? 

sensor_offsets = {
    "a": -1.175, 
    "b": -0.35,
    "c": 0.0, # Tracking val 
    "d": 0.35,
    "e": 0.0, # Tracking val 
    "f": 1.5,
}
def read_sensor_offsets():
    # global sensconf_names 
    sensoffset_path = "/home/pi/dev/ghouse/datacollection/sensor_offsets"
    sensor_offsets = {    }
    with open(sensoffset_path, 'r') as file:
        for line in file:
            devid, offset = line.split('=')
            devid = devid.strip()
            offset  = offset.strip()
            sensor_offsets[devid] = float(offset)
    return sensor_offsets

sensor_offsets = read_sensor_offsets()

""" Plotting """

sensor_plot_order = ['a', 'b', 'c', 'd', 'e', "f"]
fig, axs = plt.subplots(1, 1, figsize=(4, 3), dpi=300)

axs = [axs]

axs[0].set_xlabel("Time")
axs[0].set_ylabel("Temperature (°C)")
axs[0].set_ylim(18, 23)
# TODO: filter for time range to plot 
# set x lim (0) to be 1 day before and 1 day after 

# Plot each sensor
for i, sensor_name in enumerate(sensor_plot_order):
    axs[0].plot(df["Time"], df[sensor_name] + sensor_offsets[sensor_name], label=sensor_name, marker='o', markersize=2)

# Add vertical lines for the start of each day
# for day in pd.date_range(start=df["Time"].min().normalize(), end=df["Time"].max().normalize(), freq='D'):
#     axs[0].axvline(day, color='grey', linestyle='--', linewidth=0.8)
#     axs[0].text(day, axs[0].get_ylim()[1]- 2.5, day.strftime('%d-%m'), color='black', fontsize=8, verticalalignment='bottom')

axs[0].xaxis.set_major_locator(mdates.HourLocator(interval=6))
axs[0].xaxis.set_major_formatter(mdates.DateFormatter('%H'))

# Legend 
axs[0].legend(loc=(1.0, 0.2), fontsize=8, frameon=False, title="Sensors", title_fontsize=8)

now = datetime.datetime.now()
# Add timestamp to the figure
axs[0].set_title(now.strftime('%Y-%m-%d %H:%M:%S'))
axs[0].set_xlim(datetime.datetime(now.year, now.month, now.day, 0, 0, 0))

# axs[0].set_xlim(datetime.datetime(2025, 5, 21, 1, 0, 0), datetime.datetime(2025, 5, 21, 5, 0, 0))

# save figure 
SAVEPATH = "/home/pi/dev/ghouse/datavisualisation/figures/"
fig.savefig(SAVEPATH + "temp_plot.png", dpi=300, bbox_inches='tight')

print("Figure saved to: " + SAVEPATH + "temp_plot.png")
print(now)
