#!/home/pi/dev/ghouse/.venv/bin/python3

import pandas as pd 
import numpy as np 

import requests 
import datetime 
from time import strftime, gmtime
import xml.etree.ElementTree as ET
# valid_string = "https://opendata.fmi.fi/wfs?service=WFS&version=2.0.0&request=getFeature&storedquery_id=fmi::observations::weather::multipointcoverage&place=Kumpula&starttime=2025-01-21T00:00:00Z&endtime=2025-01-21T23:59:59Z&parameters=t2m"

FINLAND_OFFSET = 2 * 3600  # 2 hours in seconds

def get_kumpula_temperature_data_for_a_given_day(query_day: str = None): 
    url = "https://opendata.fmi.fi/wfs"
    if query_day is None:
        DAYSTART = datetime.datetime.now()
        DAYSTART = datetime.datetime(DAYSTART.year, DAYSTART.month, DAYSTART.day, 0, 0, 0)
    else: 
        DAYSTART = datetime.datetime.strptime(query_day, '%Y-%m-%d')
        DAYSTART = datetime.datetime(DAYSTART.year, DAYSTART.month, DAYSTART.day, 0, 0, 0)
    
    DAYSTART = DAYSTART - datetime.timedelta(seconds=FINLAND_OFFSET)
    DAYEND   = DAYSTART + datetime.timedelta(days=1) - datetime.timedelta(seconds=1)

    params = {
        'service': 'WFS',
        'version': '2.0.0',
        'request': 'getFeature',
        'storedquery_id': 'fmi::observations::weather::multipointcoverage',
        'place': 'Kumpula',
        "starttime": DAYSTART.isoformat() + 'Z',
        "endtime": DAYEND.isoformat() + 'Z',
        'parameters': 't2m',
    }

    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the XML response
        root = ET.fromstring(response.content)
        # Define the namespace mappings
        ns = {
            'gmlcov': 'http://www.opengis.net/gmlcov/1.0',
            'gml': 'http://www.opengis.net/gml/3.2',
        }
        
        # Extract positions and temperatures
        positions_element = root.find('.//gmlcov:positions', ns)
        temperatures_element = root.find('.//gml:doubleOrNilReasonTupleList', ns)

        if positions_element is not None and temperatures_element is not None:
            # Get the positions and temperatures as lists
            positions = positions_element.text.split()
            temperatures = temperatures_element.text.split()

            # Extract timestamps and temperatures
            timestamps = positions[2::3]  # Every third value starting at index 2
            # print(len(positions) // 3)
            temperatures = [float(temp) for temp in temperatures]
            timestamps = [strftime('%Y-%m-%d %H:%M:%S', gmtime(int(timestamp) + FINLAND_OFFSET)) for timestamp in timestamps]
            # print(timestamps)
            # print(temperatures)
            # Convert timestamps to human-readable format
            # for timestamp, temperature in zip(timestamps, temperatures):
                # dt = datetime.utcfromtimestamp(int(timestamp))
                # dt = strftime('%Y-%m-%d %H:%M:%S', gmtime(int(timestamp)))
                # print(f"Time: {timestamp}, Temperature: {temperature}°C")

            todays_dataframe = pd.DataFrame.from_dict({'Time': timestamps, 'TempKumpula': temperatures})
        else:
            print("Could not find the required elements in the XML.")
    else:
        print(f'Error: {response.status_code}')

    return todays_dataframe

if __name__ == "__main__": 
    # Get today's date
    today = datetime.datetime.now()
    today_str = today.strftime('%Y-%m-%d')
    print("Today's date:", today_str)
    
    # Call the function with today's date
    df = get_kumpula_temperature_data_for_a_given_day(today_str)
    print(df.head())
    print(df.tail())
    
    # Save the DataFrame to a CSV file
    SAVEPATH = f"/home/pi/dev/ghouse/data/external/{today_str}_fmi_kumpula.csv"
    df.to_csv(SAVEPATH)
    print(f"Data saved to {SAVEPATH}")
