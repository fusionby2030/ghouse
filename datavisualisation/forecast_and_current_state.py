#!/home/pi/dev/ghouse/.venv/bin/python3

import pandas as pd 
import matplotlib.pyplot as plt
import scienceplots 
plt.style.use(['science', 'no-latex', 'high-vis'])
import datetime 
import matplotlib.dates as mdates

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

tmp_out_cols = ["Air temperature (degC)"]
rad_out_cols = ["Diffuse radiation (W/m2)","Direct solar radiation (W/m2)","Global radiation (W/m2)", "Sunshine duration (s)"]
forecast_cols = ["temperature (°C)","cloud_cover (%)","precipitation_amount (mm/h)","wind_speed (m/s)"]

fig, axs = plt.subplots(1, 1, figsize=(4, 3), dpi=300, sharex=True)
axs = [axs]

# just plot the temperature inside for each sensor, 
# and outisde temperature
# and forecasted temperature

sensor_plot_order = ['a', 'b', 'c', 'd', 'e', "f"]
axs[0].set_xlabel("Time")
axs[0].set_ylabel("Temperature (°C)")
axs[0].set_ylim(-15, 30)
axs[0].set_xlim(YESTERDAY, TODAY + datetime.timedelta(days=1))

for i, sensor_name in enumerate(sensor_plot_order):
    axs[0].plot(df_inside["Time"], df_inside[sensor_name], label=sensor_name, marker='o', markersize=2)
axs[0].plot(df_tmp_out["Time"], df_tmp_out[tmp_out_cols[0]], label="Outside", marker='o', markersize=2)
axs[0].plot(df_forecast["Time"], df_forecast[forecast_cols[0]], label="Forecast", marker='o', markersize=2)


vlines_to_plot = [datetime.datetime(day.year, day.month, day.day, 0, 0, 0) for day in [YESTERDAY, TODAY, TOMORROW]]

for day in vlines_to_plot:
    if day > TOMORROW or day < YESTERDAY:
        continue 
    axs[0].axvline(day, color='grey', linestyle='--', linewidth=0.8)
    axs[0].text(day, axs[0].get_ylim()[1]+ 0.8, day.strftime('%d-%m'), color='black', fontsize=8, verticalalignment='bottom')


axs[0].axvline(TODAY, color='red', linestyle='--', linewidth=0.8)
axs[0].text(TODAY - datetime.timedelta(hours=1.5), axs[0].get_ylim()[1]+ 0.8, "NOW", color='red', fontsize=8, verticalalignment='bottom')

axs[0].legend(loc=(1.0, 0.2), fontsize=8, frameon=False)
axs[0].xaxis.set_major_locator(mdates.HourLocator(interval=6))
axs[0].xaxis.set_major_formatter(mdates.DateFormatter('%H'))

fig.suptitle(f"{TODAY.strftime('%Y-%m-%d %H:%M:%S')}", fontsize=8, y=1.0)

# SAVEPATH = f"/home/pi/dev/ghouse/datavisualisation/figures/{TODAY.strftime('%Y-%m-%d')}_fmi_kumpula_temperature_radiation_forecast.png"
SAVEPATH = "/home/pi/dev/ghouse/datavisualisation/figures/current_ghouse_state.png"
plt.savefig(SAVEPATH, dpi=300, bbox_inches='tight')
