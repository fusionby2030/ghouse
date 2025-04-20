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

FNAME_INSIDE = f"/home/pi/dev/ghouse/data/internal/tempdata.csv"
FNAME_TMP_OUT = f"/home/pi/dev/ghouse/data/external/2025-04-20_fmi_kumpula_temperature.csv"
FNAME_RAD_OUT = f"/home/pi/dev/ghouse/data/external/2025-04-20_fmi_kumpula_radiation.csv"
FNAME_FORECAST = f"/home/pi/dev/ghouse/data/external/2025-04-20-2025-04-21_fmi_kumpula_forecast.csv"

df_inside = pd.read_csv(FNAME_INSIDE, sep=",", header=0, names=["Time", " a", " b", " c", " d", " e", " f", " "])
df_inside = df_inside.drop(columns=[" "])
df_inside.columns = df_inside.columns.str.strip()
df_inside["Time"] = pd.to_datetime(df_inside["Time"], format="%Y-%m-%d %H:%M:%S.%f")

df_tmp_out = pd.read_csv(FNAME_TMP_OUT, sep=",")
df_tmp_out["Time"] = pd.to_datetime(df_tmp_out["Time"], format="%Y-%m-%d %H:%M:%S")
df_rad_out = pd.read_csv(FNAME_RAD_OUT, sep=",")
df_rad_out["Time"] = pd.to_datetime(df_rad_out["Time"], format="%Y-%m-%d %H:%M:%S")
df_forecast = pd.read_csv(FNAME_FORECAST, sep=",")
df_forecast["Time"] = pd.to_datetime(df_forecast["Time"], format="%Y-%m-%d %H:%M:%S")

tmp_out_cols = ["Air temperature (degC)"]
rad_out_cols = ["Diffuse radiation (W/m2)","Direct solar radiation (W/m2)","Global radiation (W/m2)", "Sunshine duration (s)"]
#forecast cols temperature (°C),cloud_cover (%),precipitation_amount (mm/h),wind_speed (m/s)
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

# Plot each sensor
for i, sensor_name in enumerate(sensor_plot_order):
    axs[0].plot(df_inside["Time"], df_inside[sensor_name], label=sensor_name, marker='o', markersize=2)
# Plot the outside temperature
axs[0].plot(df_tmp_out["Time"], df_tmp_out[tmp_out_cols[0]], label="Outside", marker='o', markersize=2)
# Plot the forecasted temperature
axs[0].plot(df_forecast["Time"], df_forecast[forecast_cols[0]], label="Forecast", marker='o', markersize=2)
# Plot the radiation data
axs[0].xaxis.set_major_locator(mdates.HourLocator(interval=6))
axs[0].xaxis.set_major_formatter(mdates.DateFormatter('%H'))

for day in pd.date_range(start=df_inside["Time"].min().normalize(), end=df_inside["Time"].max().normalize(), freq='D'):
    axs[0].axvline(day, color='grey', linestyle='--', linewidth=0.8)
    axs[0].text(day, axs[0].get_ylim()[1]- 2.5, day.strftime('%d-%m'), color='black', fontsize=8, verticalalignment='bottom')
for day in pd.date_range(start=df_forecast["Time"].min().normalize(), end=df_forecast["Time"].max().normalize(), freq='D'):
    axs[0].axvline(day, color='grey', linestyle='--', linewidth=0.8)
    axs[0].text(day, axs[0].get_ylim()[1]- 2.5, day.strftime('%d-%m'), color='black', fontsize=8, verticalalignment='bottom')

TODAY = datetime.datetime.now()
# draw vline curent time 
axs[0].axvline(TODAY, color='red', linestyle='--', linewidth=0.8, label='Now')

axs[0].legend(loc=(1.0, 0.2), fontsize=8, frameon=False)

SAVEPATH = f"/home/pi/dev/ghouse/datavisualisation/figures/{TODAY.strftime('%Y-%m-%d')}_fmi_kumpula_temperature_radiation_forecast.png"
plt.savefig(SAVEPATH, dpi=300, bbox_inches='tight')
