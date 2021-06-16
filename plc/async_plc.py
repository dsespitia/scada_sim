#!/usr/bin/env python

# SCADA Simulator
#


"""
Asynchronous PyModbus Server with Client Functionality
  Used for SCADASim 2.0
"""

# --------------------------------------------------------------------------- #
# import the modbus libraries we need
# --------------------------------------------------------------------------- #
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.version import version
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext
from pymodbus.datastore import ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer
from pymodbus.transaction import ModbusAsciiFramer
from pymodbus.transaction import ModbusBinaryFramer
from pymodbus.server.asynchronous import StartSerialServer
from pymodbus.server.asynchronous import StartTcpServer
from pymodbus.server.asynchronous import StartUdpServer
# --------------------------------------------------------------------------- #
# import the other libraries we need
# --------------------------------------------------------------------------- #
from datastore import *
from helper import *
from threading import Thread

import sys
import yaml
import time
import logging
import argparse

"""
@brief reads from backup, initializes the datastore, 
starts the backup thread and the register behavior threads, 
then starts the server
"""


def run_updating_server(config_list, backup_filename, log):
    """
    # initialize your data store

    # Run datastore_backup_on_start to use the most recent values of the
     datablocks, as the layout in the master config will only reflect
     initial values.
    # If this is the first time this is used, the backup file will match up
    with what is laid out in the master config (due to master.py)"""

    datastore_config = datastore_backup_on_start(backup_filename)

    # initialize the server information for default
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Pymodbus'
    identity.ProductCode = 'PM'
    identity.VendorUrl = 'http://github.com/riptideio/pymodbus/'
    identity.ProductName = 'Pymodbus Server'
    identity.ModelName = 'Pymodbus Server'
    identity.MajorMinorRevision = version.short()

    if datastore_config == -1:
        print("Issue with backup file - either not created or empty."
              " Exiting program.")
        sys.exit()
    
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(datastore_config['di']['start_addr'],
                                     datastore_config['di']['values']),
        co=ModbusSequentialDataBlock(datastore_config['co']['start_addr'],
                                     datastore_config['co']['values']),
        hr=ModbusSequentialDataBlock(datastore_config['hr']['start_addr'],
                                     datastore_config['hr']['values']),
        ir=ModbusSequentialDataBlock(datastore_config['ir']['start_addr'],
                                     datastore_config['ir']['values']))
    """ Could have multiple slaves, with their own addressing. 
    Since we have 1 PLC device handled by every async_plc.py, 
    it is not necessary"""
    context = ModbusServerContext(slaves=store, single=True)

    """ Setup a thread with target as datastore_backup_to_yaml to start here,
     before other threads this will continuously read from the context to 
     write to a backup yaml file"""
    backup_thread = Thread(target=datastore_backup_to_yaml,
                           args=(context, backup_filename))
    backup_thread.daemon = True
    backup_thread.start()
 
    """ Start register behaviors. Updating writer is started off, 
    which will spawn a thread for every holding register based on the config"""
    thread = Thread(target=updating_writer, args=(
        context, config_list, time.time, log, backup_filename))
    thread.daemon = True
    thread.start()

    # Starting the server
    server_config = config_list['SERVER']
    framer = configure_server_framer(server_config)
    if server_config['type'] == 'serial':
        StartSerialServer(context, port=server_config['port'], framer=framer)
    elif server_config['type'] == 'udp':
        StartUdpServer(context, identity=identity, address=(
            server_config['address'], int(server_config['port'])))
    elif server_config['type'] == 'tcp':
        if server_config['framer'] == 'RTU':
            StartTcpServer(context, identity=identity, address=(
                server_config['address'], int(server_config['port'])),
                           framer=framer)
        else:
            StartTcpServer(context, address=(
                server_config['address'], int(server_config['port'])))

"""
@brief parse args, handle master config, setup logging, 
then call run_updating_server
"""


def main():
    # --- BEGIN argparse handling ---
    parser = argparse.ArgumentParser(
        description="Main program for PLC device based off PyModbus")
    parser.add_argument("--n",
                        "--num_of_PLC",
                        help="The number of the PLC device")
    parser.add_argument("--c",
                        "--config_filename",
                        help="Name of the master config file")
    args = parser.parse_args()
    if args.n is None or args.c is None:
        print("Need to run async_plc.py with --n and --c arguments."
              " Run 'python async_plc.py --h' for help")
        return
    print(args)
    num_of_PLC = args.n
    master_config_filename = args.c
    backup_filename = '/home/dsespitia/Scripts/python/SCADASim/backups/' \
                      'backup_' + args.n + '.yaml'
    # --- END argparse handling ---

    stream = open(master_config_filename, 'r')
    config_list = yaml.safe_load(stream)
    stream.close()
    # Only get the current PLC's configuration dictionary
    config_list = config_list["PLC " + num_of_PLC]

    # --- BEGIN LOGGING SETUP ---
    FORMAT = config_list['LOGGING']['format']
    # Add logic based on whether a file is used or stdout
    #   AND whether a format string is used or not
    if config_list['LOGGING']['file'] == 'STDOUT':
        if FORMAT == 'NONE':
            logging.basicConfig()
        else:
            logging.basicConfig(format=FORMAT)
    else:
        if FORMAT == 'NONE':
            logging.basicConfig(filename=config_list['LOGGING']['file'])
        else:
            logging.basicConfig(format=FORMAT,
                                filename=config_list['LOGGING']['file'])
    log = logging.getLogger()
    configure_logging_level(config_list['LOGGING']['logging_level'], log)
    # --- END LOGGING SETUP ---
    run_updating_server(config_list, backup_filename, log)


if __name__ == "__main__":
    main()
