#!/usr/bin/python
import os
import glob
from datetime import datetime
import time

writeorder = ['a', 'b', 'c', 'd', 'e', "f"]
w1devicespath = "/sys/bus/w1/devices/"
writepath = "/home/pi/dev/ghouse/datacollection/tempdata.csv"

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
    pass 

def run_collect():
    collect_time = datetime.now()
    collected_data = read_all_devices()
    write_data(collected_data, collect_time)
    
if __name__ == "__main__":
    read_sensor_names()
    print(sensconf_names)
    # collect_time = datetime.now()
    # print(collect_time)
    # collected_data = read_all_devices()
    # print(collected_data)
    # write_data(collected_data, collect_time)

    # while True:
    run_collect()
    # time.sleep(60)
