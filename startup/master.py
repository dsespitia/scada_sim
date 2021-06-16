#!/usr/bin/env python

# SCADA Simulator

import sys
import yaml
from os import path

# (Default) open txt file to get config.yaml file name IF path of config
# file was not supplied as argument to master.py
# strip any trailing /n from string
if len(sys.argv) == 1:
    with open("/usr/local/bin/scadasim_pymodbus_plc/"
              "startup/config_file_name.txt", 'r') as f:
        file_name = f.read()
        file_name = file_name.rstrip()
else:
    file_name = sys.argv[1]

# open yaml config file, build object
with open(file_name, 'r') as config_file:
    config_yaml = yaml.safe_load(config_file)

# get number of plc devices from MASTER section of the config file
num_of_plc = config_yaml['MASTER']['num_of_PLC']
# create backup files if they do not already exist - 1 for each PLC device
i = 0
while i < num_of_plc:
    num = str(i)
    plc_device_name = 'PLC ' + num
    # keep in the src repo, in format of "backup_N.yaml",
    # where N is the ID of the PLC device
    backup_file = '/usr/local/bin/scadasim_pymodbus_plc/backups/backup_' \
                  + num + '.yaml'
    
    # collect num of register/coils for each plc device
    hr_values = config_yaml[plc_device_name]['DATASTORE']['hr']['values']
    co_values = config_yaml[plc_device_name]['DATASTORE']['co']['values']
    di_values = config_yaml[plc_device_name]['DATASTORE']['di']['values']
    ir_values = config_yaml[plc_device_name]['DATASTORE']['ir']['values']

    # check if file exists
    if not path.exists(backup_file) or path.getsize(backup_file) == 0:
        # create file - only storing the register starting address and values 
        backup_dict = {}
        with open(backup_file, 'w+') as backup:
            backup_dict['DATASTORE'] = {
                'hr': {'start_addr': 1, 'values': hr_values},
                'ir': {'start_addr': 1, 'values': ir_values},
                'co': {'start_addr': 1, 'values': co_values},
                'di': {'start_addr': 1, 'values': di_values}}
            yaml.dump(backup_dict, backup)
    i = i + 1

# return number of backup files created and the config
# filepath to bash startup script
print(str(num_of_plc) + ' ' + file_name)
