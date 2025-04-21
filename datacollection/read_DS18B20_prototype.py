#!/usr/bin/python
import os
import glob
from datetime import datetime
import time

writeorder = ['a', 'b', 'c', 'd', 'e', "f"]
w1devicespath = "/sys/bus/w1/devices/"
writepath = "/home/pi/dev/ghouse/datacollection/tempdata.csv"
writepath = "/home/pi/dev/ghouse/data/internal/tempdata.csv"

def read_sensor_names():
    global sensconf_names 
    sensconf_path = "/home/pi/dev/ghouse/datacollection/sensor_names"
    sensconf_names = {    }
    with open(sensconf_path, 'r') as file:
        for line in file:
            print(line)
            devid, name = line.split('=')
            devid = devid.strip()
            name  = name.strip()
            sensconf_names[devid] = name

def read_sensor_offsets():
    global sensor_offsets 
    sensoffset_path = "/home/pi/dev/ghouse/datacollection/sensor_offsets"
    sensor_offsets = {    }
    with open(sensoffset_path, 'r') as file:
        for line in file:
            devid, offset = line.split('=')
            devid = devid.strip()
            offset  = offset.strip()
            sensor_offsets[devid] = float(offset)
    return sensor_offsets

def read_all_devices():
    avail_devices = glob.glob(w1devicespath + '*')
    collected_data = {key: None for key in sensconf_names.keys()}
    for _dir in avail_devices:
        _devid = _dir.split('/')[-1]
        if _devid not in sensconf_names:
            continue
        
        print("Found ", _devid, sensconf_names[_devid])
        datapath = os.path.join(_dir, "w1_slave")
    
        with open(datapath, 'r') as file:
            lines = file.readlines()
            success = "YES" in lines[0]
            temp = float(lines[1].split('=')[-1]) / 1000.0
            
        collected_data[_devid] = temp
    return collected_data

def offset_collected_data(collected_data):
    # offset the collected data
    print("offsetting data from \'sensor_offsets\'")
    for devid in collected_data.keys(): 
        # print("Before offsetting: ", devid, collected_data[devid])
        offset = sensor_offsets[devid]
        collected_data[devid] += offset
        # print("After offsetting: ", devid, collected_data[devid])
    return collected_data 


def write_data(collected_data, timestamp):
    # build the write string
    
    newline = f"{timestamp},"
    for name in writeorder:
        written = False
        for devid, _name in sensconf_names.items():
            if name == _name:
                newline += f'{collected_data[devid]:6},'
                written = True
        if not written:
            newline += "None, "
    print(newline)
    newline += "\n"
    with open(writepath, 'a') as file:
        
        file.write(newline)

def run_collect():
    collect_time = datetime.now()
    collected_data = read_all_devices()
    collected_data = offset_collected_data(collected_data)
    # write_data(collected_data, collect_time)
    print(f"{collect_time} saved to {writepath}")
if __name__ == "__main__":
    read_sensor_names()
    read_sensor_offsets()
    print(sensconf_names)
    print(sensor_offsets)
    run_collect()
    