#!/home/pi/dev/ghouse/.venv/bin/python3

import pandas as pd 
import matplotlib.pyplot as plt
import scienceplots 
plt.style.use(['science', 'no-latex'])
import datetime 
import matplotlib.dates as mdates


TODAY = datetime.datetime.now()

# /home/pi/dev/ghouse/data/external/2025-04-20_fmi_kumpula_temperature.csv

FNAME_TEMP = f"/home/pi/dev/ghouse/data/external/{TODAY.strftime('%Y-%m-%d')}_fmi_kumpula_temperature.csv"
FNAME_RAD  = f"/home/pi/dev/ghouse/data/external/{TODAY.strftime('%Y-%m-%d')}_fmi_kumpula_radiation.csv"

df_temp = pd.read_csv(FNAME_TEMP, sep=",")
df_rad  = pd.read_csv(FNAME_RAD, sep=",")

# Convert the time column to datetime
df_temp["Time"] = pd.to_datetime(df_temp["Time"], format="%Y-%m-%d %H:%M:%S")
df_rad["Time"] = pd.to_datetime(df_rad["Time"], format="%Y-%m-%d %H:%M:%S")

temp_cols = ["Air temperature (degC)"]

rad_cols = ["Diffuse radiation (W/m2)","Direct solar radiation (W/m2)","Global radiation (W/m2)", "Sunshine duration (s)"]

fig, axs = plt.subplots(len(temp_cols) + len(rad_cols), 1, figsize=(4, len(temp_cols) + len(rad_cols) * 3), dpi=300, sharex=True)

for i, col in enumerate(temp_cols):
    name, unit = col.split("(")
    unit = unit.strip(") ")

    # axs[i].set_title(name)
    axs[i].text(0.5, 0.9, name, ha='left', va='center', transform=axs[i].transAxes, fontsize=12)
    axs[i].set_ylabel(f"{unit}")
    axs[i].scatter(df_temp["Time"], df_temp[col], label=col, marker='o', s=2)
    # axs[i].legend(loc=(1.0, 0.2), fontsize=8, frameon=False, title="Sensors", title_fontsize=8)

for i, col in enumerate(rad_cols):
    name, unit = col.split("(")
    unit = unit.strip(") ")
    axs[i + len(temp_cols)].set_title(name)
    axs[i + len(temp_cols)].set_ylabel(f"{unit}")
    axs[i + len(temp_cols)].scatter(df_rad["Time"], df_rad[col], label=col, marker='o', s=2)

axs[0].set_ylim(-15, 30)
axs[0].xaxis.set_major_locator(mdates.HourLocator(interval=6))
axs[0].xaxis.set_major_formatter(mdates.DateFormatter('%H'))


SAVEPATH = f"/home/pi/dev/ghouse/datavisualisation/figures/{TODAY.strftime('%Y-%m-%d')}_fmi_kumpula_temperature_radiation.png"
plt.savefig(SAVEPATH, dpi=300, bbox_inches='tight')


print(f"Figure saved to {SAVEPATH}")
print(TODAY)