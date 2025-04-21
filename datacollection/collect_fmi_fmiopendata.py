#!/home/pi/dev/ghouse/.venv/bin/python3
# https://en.ilmatieteenlaitos.fi/guidance-to-observations
import datetime as dt 
from fmiopendata.wfs import download_stored_query 
import pandas as pd 

FINLAND_OFFSET = 3 * 3600  # 3 hours for SUMMER time, 2 hours for WINTER time


def get_temperature_data_for_times(start_time, end_time): 
    # Convert times to properly formatted strings
    start_time = start_time.isoformat(timespec="seconds") + "Z" # -> 2020-07-07T12:00:00Z
    end_time = end_time.isoformat(timespec="seconds") + "Z" # -> 2020-07-07T13:00:00Z

    collected_data = {}

    obs = download_stored_query("fmi::observations::weather::multipointcoverage",
                                args=["place=Kumpula",
                                    f"starttime={start_time}",
                                        f"endtime={end_time}",
                                    ])
    latest_tstep = max(obs.data.keys())

    data_keys_interest = ['Air temperature', 'Cloud amount', 'Dew-point temperature', 'Wind direction', 'Wind speed', 'Relative humidity', 'Precipitation amount']

    for num, (timestep_key, timestep_data) in enumerate(obs.data.items()):
        collected_data[num] = {}
        # add the finland offset to the timestep key 
        offset_time = timestep_key + dt.timedelta(seconds=FINLAND_OFFSET)

        collected_data[num]['Time'] = offset_time.strftime("%Y-%m-%d %H:%M:%S")

        for key in data_keys_interest:
            # print(timestep_data['Helsinki Kumpula'][key])
            named_key = key + f" ({timestep_data['Helsinki Kumpula'][key]['units']})"
            collected_data[num][named_key] = timestep_data['Helsinki Kumpula'][key]['value'].item()

    temp_df = pd.DataFrame.from_dict(collected_data, orient='index')
    return temp_df 

def get_kumpula_radiation_data_for_times(start_time, end_time): 
    start_time = start_time.isoformat(timespec="seconds") + "Z" # -> 2020-07-07T12:00:00Z
    end_time = end_time.isoformat(timespec="seconds") + "Z" # -> 2020-07-07T13:00:00Z

    collected_data = {}
    obs_rad = download_stored_query("fmi::observations::radiation::multipointcoverage",
                                args=["place=Kumpula",
                                    f"starttime={start_time}",
                                        f"endtime={end_time}",
                                    ])

    latest_tstep_rad = max(obs_rad.data.keys())
    data_keys_interest = ['Diffuse radiation', 'Direct solar radiation', 'Global radiation', 'Long wave outgoing solar radiation', 'Long wave solar radiation ', 'Radiation balance', 'Reflected radiation', 'Sunshine duration', 'Ultraviolet irradiance']

    for num, (timestep_key, timestep_data) in enumerate(obs_rad.data.items()):
        collected_data[num] = {}
        offset_time = timestep_key + dt.timedelta(seconds=FINLAND_OFFSET)
        collected_data[num]['Time'] = offset_time.strftime("%Y-%m-%d %H:%M:%S")

        for key in data_keys_interest:
            named_key = key + f" ({timestep_data['Helsinki Kumpula'][key]['units']})"
            collected_data[num][named_key] = timestep_data['Helsinki Kumpula'][key]['value'].item()
    temp_df_rad = pd.DataFrame.from_dict(collected_data, orient='index')
    return temp_df_rad

if __name__ == "__main__": 
    today = dt.datetime.now()
    today_str = today.strftime('%Y-%m-%d')

    DAYSTART = dt.datetime(today.year, today.month, today.day, 0, 0, 0)
    DAYSTART = DAYSTART - dt.timedelta(seconds=FINLAND_OFFSET)
    DAYEND   = DAYSTART + dt.timedelta(days=1) - dt.timedelta(seconds=1)

    print("Today's date:", today_str)
    # end_time = dt.datetime.utcnow()
    # start_time = dt.datetime(end_time.year, end_time.month, end_time.day, 0, 0, 0) 
    
    start_time = DAYSTART 
    end_time = DAYEND
    temp_df = get_temperature_data_for_times(start_time, end_time)
    temp_df_rad = get_kumpula_radiation_data_for_times(start_time, end_time)

    print(temp_df.head())
    print(temp_df.tail())


    print(temp_df_rad.head())
    print(temp_df_rad.tail())

    SAVEPATH = f"/home/pi/dev/ghouse/data/external/{today_str}_fmi_kumpula_temperature.csv"
    SAVEPATH_RAD = f"/home/pi/dev/ghouse/data/external/{today_str}_fmi_kumpula_radiation.csv"
    # Save the DataFrame to a CSV file
    temp_df.to_csv(SAVEPATH, index=False)
    temp_df_rad.to_csv(SAVEPATH_RAD, index=False)

    print("Data saved to: " + SAVEPATH)
    print("Data saved to: " + SAVEPATH_RAD)
