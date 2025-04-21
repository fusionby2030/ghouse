#!/home/pi/dev/ghouse/.venv/bin/python3

import pandas as pd 
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
import scienceplots 
plt.style.use(['science', 'no-latex', 'high-vis'])
import datetime 
import matplotlib.dates as mdates
import numpy as np 

""" 
Plot the measured temperatures, 
the outside state, 
and the forecasted temperatures
"""

TODAY = datetime.datetime.now()
YESTERDAY = TODAY - datetime.timedelta(days=1)
TOMORROW = TODAY + datetime.timedelta(days=1)


FNAME_INSIDE = f"/home/pi/dev/ghouse/data/internal/tempdata.csv"
# f"/home/pi/dev/ghouse/data/external/2025-04-20_fmi_kumpula_temperature.csv"
fnames_tmp_outside = [f"/home/pi/dev/ghouse/data/external/{DAY}_fmi_kumpula_temperature.csv" for DAY in [YESTERDAY.strftime('%Y-%m-%d'), TODAY.strftime('%Y-%m-%d')]]
# f"/home/pi/dev/ghouse/data/external/2025-04-20_fmi_kumpula_radiation.csv"
fnames_rad_outside = [f"/home/pi/dev/ghouse/data/external/{DAY}_fmi_kumpula_radiation.csv" for DAY in [YESTERDAY.strftime('%Y-%m-%d'), TODAY.strftime('%Y-%m-%d')]]
FNAME_FORECAST = f"/home/pi/dev/ghouse/data/external/24hr_forecast_fmi_kumpula.csv"

# Read the data from the CSV files
df_inside = pd.read_csv(FNAME_INSIDE, sep=",", header=0, names=["Time", " a", " b", " c", " d", " e", " f", " "])
df_inside = df_inside.drop(columns=[" "])
df_inside.columns = df_inside.columns.str.strip()
df_inside["Time"] = pd.to_datetime(df_inside["Time"], format="%Y-%m-%d %H:%M:%S.%f")

df_tmp_out = []
for FNAME_TMP_OUT in fnames_tmp_outside:
    _df_tmp_out = pd.read_csv(FNAME_TMP_OUT, sep=",")
    _df_tmp_out["Time"] = pd.to_datetime(_df_tmp_out["Time"], format="%Y-%m-%d %H:%M:%S")
    df_tmp_out.append(_df_tmp_out)
df_tmp_out = pd.concat(df_tmp_out, ignore_index=True)

df_rad_out = []
for FNAME_RAD_OUT in fnames_rad_outside:
    _df_rad_out = pd.read_csv(FNAME_RAD_OUT, sep=",")
    _df_rad_out["Time"] = pd.to_datetime(_df_rad_out["Time"], format="%Y-%m-%d %H:%M:%S")
    df_rad_out.append(_df_rad_out)
df_rad_out = pd.concat(df_rad_out, ignore_index=True)

df_forecast = pd.read_csv(FNAME_FORECAST, sep=",")
df_forecast["Time"] = pd.to_datetime(df_forecast["Time"], format="%Y-%m-%d %H:%M:%S")

tmp_out_cols = ["Air temperature (degC)", "Precipitation amount (mm)", "Cloud amount (1/8)"]

forecast_cols = ["temperature (°C)","cloud_cover (%)","precipitation_amount (mm/h)","wind_speed (m/s)"]

fig = plt.figure(figsize=(12, 12), dpi=300)

"""
------------------------------------ 
|           |          |           |
|           |          |           |
|           |          |           |
------------------------------------ 
|           |          |           |
|           |          |           |
|           |          |           |
------------------------------------
|           |          |           |
|           |          |           |
|           |          |           |
------------------------------------
"""

gs = GridSpec(3, 3, figure=fig)

axs_temp_all = fig.add_subplot(gs[0:2, 1:])
axs_rad      = fig.add_subplot(gs[0, 0])
axs_sunshine = fig.add_subplot(gs[1, 0])
axs_percip   = fig.add_subplot(gs[2, 0])
axs_lamp     = fig.add_subplot(gs[2, 1])
axs_fans     = fig.add_subplot(gs[2, 2])

axs = [axs_temp_all, axs_rad, axs_sunshine, axs_percip, axs_lamp, axs_fans]

""" 
On axs_temp_all -> plot temperature inside (sensors), outside (fmi) and forecast 
On axs_rad -> plot radiation outside (fmi)
    --- Diffuse Radiation, Direct solar radaition, Global radiation 
On axs_sunshine -> plot sunshine duration outside (fmi), cloud cover (fmi), cloud cover forecast (fmi)
    --- Sunshine duration

On axs_percip -> plot precipitation amount outside (fmi), forecast 
TODO: wind speed outside 
"""

sensor_plot_order = ['a', 'b', 'c', 'd', 'e', "f"]
axs_temp_all.set_xlabel("Time")
axs_temp_all.set_ylabel("Temperature (°C)")
axs_temp_all.set_ylim(-15, 30)

for i, sensor_name in enumerate(sensor_plot_order):
    axs_temp_all.plot(df_inside["Time"], df_inside[sensor_name], label=sensor_name, marker='o', markersize=2)
axs_temp_all.plot(df_tmp_out["Time"], df_tmp_out[tmp_out_cols[0]], label="Outside", marker='o', markersize=2)
axs_temp_all.plot(df_forecast["Time"], df_forecast[forecast_cols[0]], label="Forecast", marker='o', markersize=2)

axs_temp_all.legend(loc=(1.0, 0.1), fontsize=8, frameon=False)



""" Radiation """ 
axs_rad.set_title("Radiation")
axs_rad.set_ylabel("(W/m2)")
rad_out_cols = ["Diffuse radiation (W/m2)","Direct solar radiation (W/m2)","Global radiation (W/m2)", "Sunshine duration (s)"]

for i, col in enumerate(rad_out_cols[:-1]):
    name, unit = col.split("(")
    unit = unit.strip(") ")
    # remove radiation from name 
    name = name.replace("radiation", "").strip()
    axs_rad.plot(df_rad_out["Time"], df_rad_out[col], label=name, marker='o', markersize=2)

axs_rad.legend(loc="upper left")

""" Sunshine """ 


axs_sunshine.set_ylabel("Sunshine duration (s)")
axs_sunshine.plot(df_rad_out["Time"], df_rad_out[rad_out_cols[-1]], label="Sunshine", color='orange', marker='o', markersize=2)
axs_sunshine.set_ylim(0, 80)
axs_sunshine.set_yticks([0, 20, 40, 60])
axs_sunshine.set_yticklabels([0, 20, 40, 60])

cloud_axs = axs_sunshine.twinx()
cloud_axs.set_ylabel("Cloud cover (%)")
cloud_axs.plot(df_tmp_out["Time"], df_tmp_out["Cloud amount (1/8)"] / 8.0, label="Cloud", color='blue', marker='o', markersize=2)
cloud_axs.set_ylim(0, 1.5)
cloud_axs.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
cloud_axs.set_yticklabels([0, 25, 50, 75, 100])

cloud_axs.plot(df_forecast["Time"], df_forecast["cloud_cover (%)"] / 100.0, label="Cloud forecast", color='red', marker='o', markersize=2)

axs_sunshine.legend(loc='upper left')
cloud_axs.legend(loc='upper right')
cloud_axs.set_title("Cloud/Sunshine")

""" Percipitation """ 
axs_percip.set_ylabel("Precipitation (mm)")
axs_percip.plot(df_tmp_out["Time"], df_tmp_out["Precipitation amount (mm)"], label="FMI Kumpula", marker='o', markersize=2)
axs_percip.plot(df_forecast["Time"], df_forecast["precipitation_amount (mm/h)"], label="Forecast", marker='o', markersize=2)

axs_percip.legend(loc='upper left')
axs_percip.set_title("Precipitation")


""" Lamp """

axs_lamp.set_title("Lamp")

# Temporary data 
time_lamp = df_inside["Time"]
data_lamp = np.zeros_like(time_lamp, dtype=int)
data_lamp[(time_lamp.dt.hour < 18) & (time_lamp.dt.hour > 6)] = 1
axs_lamp.plot(time_lamp, data_lamp, label="Lamp", marker='o', markersize=2)

# forecast 
time_lamp = df_forecast["Time"]
data_lamp = np.zeros_like(time_lamp, dtype=int)
data_lamp[(time_lamp.dt.hour < 18) & (time_lamp.dt.hour > 6)] = 1
axs_lamp.plot(time_lamp, data_lamp, label="Controller Suggest", marker='o', markersize=2, color="red")

axs_lamp.set_ylabel("Lamp (on/off)")
axs_lamp.set_ylim(-0.1, 1.85)
axs_lamp.set_yticks([0, 1])
axs_lamp.set_yticklabels(["Off", "On"])
axs_lamp.legend(loc='upper left')

""" Fans / Wind speed """ 
axs_fans.set_title("Fans/Outdoor wind speed")

axs_wind = axs_fans.twinx()
axs_wind.set_ylabel("Wind speed (m/s)")
axs_wind.plot(df_tmp_out["Time"], df_tmp_out["Wind speed (m/s)"], label="FMI Kumpula", marker='o', markersize=2)
# forecast 
axs_wind.plot(df_forecast["Time"], df_forecast["wind_speed (m/s)"], label="Forecast", marker='o', markersize=2, color="red")

axs_wind.legend(loc='upper right', title="Outdoor wind speed")
axs_wind.set_ylim(0, 10)
vlines_to_plot = [datetime.datetime(day.year, day.month, day.day, 0, 0, 0) for day in [YESTERDAY, TODAY, TOMORROW]]
for i, ax in enumerate(axs): 
    ax.set_xlim(YESTERDAY, TODAY + datetime.timedelta(days=1))
    for day in vlines_to_plot:
        if day > TOMORROW or day < YESTERDAY:
            continue 
        ax.axvline(day, color='grey', linestyle='--', linewidth=0.8)
        if i == 0: 
            ax.text(day, ax.get_ylim()[1]+ 0.8, day.strftime('%d-%m'), color='black', fontsize=12, verticalalignment='bottom')

    if i == 0: 
        ax.text(TODAY - datetime.timedelta(hours=1.5), ax.get_ylim()[1]+ 0.8, "NOW", color='red', fontsize=8, verticalalignment='bottom')
    ax.axvline(TODAY, color='red', linestyle='--', linewidth=0.8)

    # ax.legend(loc=(1.0, 0.1), fontsize=8, frameon=False)
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H'))



fig.suptitle(f"{TODAY.strftime('%Y-%m-%d %H:%M:%S')}", fontsize=20, y=0.95)
# fig.tight_layout()
# SAVEPATH = f"/home/pi/dev/ghouse/datavisualisation/figures/{TODAY.strftime('%Y-%m-%d')}_fmi_kumpula_temperature_radiation_forecast.png"
# SAVEPATH = "/home/pi/dev/ghouse/datavisualisation/figures/prototype.png"
SAVEPATH = "/home/pi/dev/ghouse/datavisualisation/figures/current_ghouse_state.png"
plt.savefig(SAVEPATH, dpi=300, bbox_inches='tight')
print(f"Figure saved to {SAVEPATH}")