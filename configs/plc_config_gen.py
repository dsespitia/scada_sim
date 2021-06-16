#!/usr/bin/env python

# SCADA Simulator
#

import sys
import yaml

"""
@brief obtain input on parameters for linear behavior
"""


def linear_behavior_setup():
    linear = dict(variance=int(input("Variance of linear function:\n")),
                  address=input(
                    "Starting address for register(s) to control:\n"),
                  time=int(input(
                    "Frequency to update register values (in seconds):\n")),
                  count=int(input("Number of registers to control:\n")))
    return linear


def linear_coil_dependent_setup():
    coil = linear_behavior_setup()
    coil['max'] = int(input("Max value of the register(s):\n"))
    coil['coil_address'] = int(
        input("Address of the coil it is dependent on:\n"))
    coil['default_coil_value'] = int(input("Default coil value - "
                                           "default state that would mean "
                                           "normal behavior:\n"))
    return coil


"""
@brief obtain input on parameters for random behavior
"""


def random_behavior_setup():
    rand = dict(min=int(input("Minimum value the register can hold:\n")),
                max=int(input("Maximum value the register can hold:\n")),
                address=input("Starting address for register(s) to "
                              "control:\n"),
                time=int(
                  input(
                      "Frequency to update register values (in seconds):\n")),
                count=int(input("Number of registers to control:\n")))
    return rand


def constant_behavior_setup():
    cons = dict(num=int(input(
        "Value that the coil register should try to stay constant at:\n")),
        address=input("Starting address for register(s) to control:\n"),
        time=int(
            input("Frequency to update register values (in seconds):\n")),
        count=int(input("Number of registers to control:\n")))
    return cons


"""
@brief obtain input to setup the datastore
"""


def datastore_setup():
    datastore_dict = {'hr': {'start_addr': 1, 'values': [1, 2, 3]},
                      'ir': {'start_addr': 1, 'values': [4, 4, 4]},
                      'co': {'start_addr': 1, 'values': [0, 0, 0]},
                      'di': {'start_addr': 1, 'values': [100, 250, 0]}}
    print("\n\nConfiguring Datastore\n")
    # holding reg setup
    start_addr = int(input("Start addr for hr?\n"))
    values = input("Initial values for hr?\n").split()
    values = list(map(int, values))
    datastore_dict['hr']['start_addr'] = start_addr
    datastore_dict['hr']['values'] = values
    for i in range(len(values)):
        datastore_dict['hr']['behavior_' + str(i + 1)] = dict()
        cur_behavior = input("Linear, linear_coil_dependent,"
                             " or random behavior?\n")
        datastore_dict['hr']['behavior_' + str(i + 1)]['type'] = cur_behavior
        if cur_behavior == "linear":
            behavior_sub_dict = linear_behavior_setup()
        elif cur_behavior == "linear_coil_dependent":
            behavior_sub_dict = linear_coil_dependent_setup()
        elif cur_behavior == "random":
            behavior_sub_dict = random_behavior_setup()
        datastore_dict['hr']['behavior_' + str(i + 1)].update(
            behavior_sub_dict)

    # input reg setup
    start_addr = int(input("Start addr for ir?\n"))
    values = input("Initial values for ir?\n").split()
    values = list(map(int, values))
    datastore_dict['ir']['start_addr'] = start_addr
    datastore_dict['ir']['values'] = values

    # coil reg setup
    start_addr = int(input("Start addr for co?\n"))
    values = input("Initial values for co?\n").split()
    values = list(map(int, values))
    datastore_dict['co']['start_addr'] = start_addr
    datastore_dict['co']['values'] = values
    for i in range(len(values)):
        datastore_dict['co']['behavior_' + str(i + 1)] = dict()
        cur_behavior = input("constant or none behavior?\n")
        datastore_dict['co']['behavior_' + str(i + 1)]['type'] = cur_behavior
        if cur_behavior == "constant":
            behavior_sub_dict = constant_behavior_setup()
            datastore_dict['co']['behavior_' + str(i + 1)].update(
                behavior_sub_dict)

    # di reg setup
    start_addr = int(input("Start addr for di?\n"))
    values = input("Initial values for di?\n").split()
    values = list(map(int, values))
    datastore_dict['di']['start_addr'] = start_addr
    datastore_dict['di']['values'] = values
    return datastore_dict


"""
@brief obtain input on logging setup
"""


def logging_setup():
    logging_dict = {'logging_level': 'DEBUG',
                    'file': 'STDOUT',
                    'format': '%(asctime)-15s %(threadName)-15s '
                              '%(levelname)-8s %(module)-15s:%(lineno)-8s '
                              '%(message)s'}
    def_format = '%(asctime)-15s %(threadName)-15s %(levelname)-8s ' \
                 '%(module)-15s:%(lineno)-8s %(message)s'
    print("\n\nConfiguring Logging\n")
    logging_dict['logging_level'] = input("Enter logging level (CRITICAL, "
                                          "ERROR, WARNING, INFO, DEBUG, "
                                          "or NOTSET) :\n")
    logging_dict['file'] = input("Enter STDOUT or valid filepath for "
                                 "logging destination:\n")
    logging_dict['format'] = input("Enter NONE, DEFAULT (for '%(asctime)-15s"
                                   " %(threadName)-15s %(levelname)-8s "
                                   "%(module)-15s:%(lineno)-8s %(message)s'), "
                                   "or a valid format string:\n")
    if logging_dict['format'] == 'DEFAULT':
        logging_dict['format'] = def_format
    return logging_dict


"""
@brief obtain input on PyModbus Server setup
"""


def server_setup():
    server_dict = dict(framer='RTU', type='serial', port='/dev/ttyS1')
    print("\n\nConfiguring Server\n")
    server_dict['type'] = input("Enter type of PyModbus server "
                                "(tcp, serial, etc):\n")
    server_dict['framer'] = input("Enter type of framer "
                                  "(TCP, RTU, ASCII, etc):\n")
    server_dict['port'] = input("Enter port used for server:\n")
    server_dict['address'] = input("Enter address used for server "
                                   "(NONE if using serial server):\n")
    return server_dict


"""
@brief calls all of the other functions - encapsulates the setup of a PLC device
"""


def plc_setup():
    return dict(DATASTORE=datastore_setup(), LOGGING=logging_setup(),
                SERVER=server_setup())


"""
@brief generates a master config file in YAML format
- Determines the number of PLC devices then calls plc_setup(), 
  which in turn calls other functions, in order to finish it up and 
  yaml.dump it to the config yaml file for later use
"""


def main():
    print("SCADASim 2.0 PLC config generator\n")

    config_dict = {'MASTER': {'num_of_PLC': 1}}
    num_devices = input("How many PLC devices? ")
    config_dict['MASTER']['num_of_PLC'] = int(num_devices)
    output_filename = input("Enter the full path of the file the "
                            "config should yaml.dump to OR enter 'DEFAULT': ")
    if output_filename == "DEFAULT":
        dump_filename = '/usr/local/bin/scadasim_pymodbus_plc' \
                        '/configs/test_generator_dump.yaml'
    else:
        dump_filename = output_filename

    if len(sys.argv) == 2:
        dump_filename = sys.argv[1]
    for i in range(int(num_devices)):
        print("\n\nConfiguring PLC " + str(i))
        config_dict["PLC " + str(i)] = plc_setup()
    print(config_dict)
    with open(dump_filename, 'w+') as stream:
        yaml.dump(config_dict, stream)


if __name__ == "__main__":
    main()
