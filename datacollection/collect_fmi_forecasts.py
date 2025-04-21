#!/home/pi/dev/ghouse/.venv/bin/python3
import datetime as dt
import pandas as pd 
import fmi_weather_client as fmi
from fmi_weather_client.errors import ClientError, ServerError

NOW = dt.datetime.now()
FINLAND_OFFSET = 3 * 3600  # 3 hours for SUMMER time, 2 hours for WINTER time

NUMHOURS = 24

UNTIL = NOW + dt.timedelta(hours=NUMHOURS)

try:
    forecast = fmi.forecast_by_coordinates(60.12, 24.57, timestep_hours=1,forecast_points=NUMHOURS)
except ClientError as err:
    print(f"Client error with status {err.status_code}: {err.message}")
except ServerError as err:
    print(f"Server error with status {err.status_code}: {err.body}")

print("Collecting data", NOW)
"""
pressure
humidity
wind_direction
wind_speed
cloud_cover
temperature
precipitation_amount
# Short wave radiation (light, UV) accumulation
radiation_short_wave_acc: Value

# Short wave radiation (light, UV) net accumulation on the surface
radiation_short_wave_surface_net_acc: Value

# Long wave radiation (heat, infrared) accumulation
radiation_long_wave_acc: Value

# Long wave radiation (light, UV) net accumulation on the surface
radiation_long_wave_surface_net_acc: Value

# Diffused short wave
radiation_short_wave_diff_surface_acc: Value

queried with 
precipitation_amount = weather_data.precipitation_amount.value 
percipitation_units  = weather_data.precipitation_amount.unit
""" 

keys_to_collect = [
    "temperature",
    "cloud_cover",
    "precipitation_amount",
    "wind_speed",
    "wind_direction",
    "humidity",
    "pressure"
]

collected_data = {}
for num, weather_data in enumerate(forecast.forecasts):
    # print(weather_data)
    
    # print(f"Temperature at {weather_data.time}: {weather_data.temperature}, {weather_data.cloud_cover}")
    collected_data[num] = {}
    for key in keys_to_collect:
        keydat = getattr(weather_data, key)
        keyval, keyunit = keydat.value, keydat.unit
        keyname = f"{key} ({keyunit})"
        collected_data[num][keyname] = keyval
    savetime = weather_data.time + dt.timedelta(seconds=FINLAND_OFFSET)

    collected_data[num]['Time'] =savetime.strftime("%Y-%m-%d %H:%M:%S")


df = pd.DataFrame.from_dict(collected_data, orient='index')
print(df.head())
print(df.tail())

FNAME = f"/home/pi/dev/ghouse/data/external/24hr_forecast_fmi_kumpula.csv"
df.to_csv(FNAME, sep=",", index=False)
print(f"{NOW} 24hr Forecast saved to {FNAME}")
