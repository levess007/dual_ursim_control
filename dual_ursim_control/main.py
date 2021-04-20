#!/usr/bin/env python

import threading
from os import wait, read
import os.path

import requests
import socket
import rtde_control
import time
import math
import openpyxl
import json
import logging
import logging.config
from xmlrpc.server import SimpleXMLRPCServer
from configparser import ConfigParser
from config import Config

# from pynput.keyboard import Listener, Key

SCRIPT_DIR = os.path.dirname(__file__)

# TODO: export these to json?
# Config file name
# CONFIG_FILE = 'path.xlsx'

CONFIG_FILE = os.path.join(SCRIPT_DIR, "path.xlsx")

CONFIG_FILE_SHEET_NAME = 'Configurations'
CONFIG_FILE_SHEET_MASTER = 'M'
CONFIG_FILE_SHEET_SLAVE = 'S'

j_speed = 0
j_acc = 0

l_speed = 0
l_acc = 0

# jogging_wait = {"Master": False, "Slave": False}
jogging_event = {
    'Master': threading.Event(),
    'Slave': threading.Event()
}

path_master = {}
path_slave = {}


def write_paths_to_json(path_master, path_slave):
    with open('waypoints_master.json', 'w') as json_file:
        json.dump(path_master, json_file, indent=4)

    with open('waypoints_slave.json', 'w') as json_file:
        json.dump(path_slave, json_file, indent=4)


def read_paths_from_json():
    with open('waypoints_master.json', 'r') as json_file:
        path_master = json.load(json_file)

    with open('waypoints_slave.json', 'r') as json_file:
        path_slave = json.load(json_file)

    return path_master, path_slave


def read_path_waypoints_from_file():
    # This reads the master and slave sheets
    # Data only, because otherwise you get references, or sums
    wb = openpyxl.load_workbook(CONFIG_FILE, data_only=True)
    sheet = wb[CONFIG_FILE_SHEET_MASTER]

    # X (mm) Y (mm) Z (mm) RX (rad) Ry (rad) Rz (rad)
    # Must divide x,y,z with magic number= 1000

    # J1 (deg) J2 (deg) J3 (deg) J4 (deg) J5 (deg) J6 (deg)
    # Must convert to radian for some reason

    path_master['CM0_P'] = [sheet['B2'].value, sheet['C2'].value, sheet['D2'].value,
                            sheet['E2'].value, sheet['F2'].value, sheet['G2'].value]
    path_master['CM0_P'][0:3] = [x / 1000.0 for x in path_master['CM0_P'][0:3]]
    logging.debug(f"CM0_P: {path_master['CM0_P']}")

    path_master['CM0_J'] = [sheet['H2'].value, sheet['I2'].value, sheet['J2'].value,
                            sheet['K2'].value, sheet['L2'].value, sheet['M2'].value]
    path_master['CM0_J'] = [math.radians(x) for x in path_master['CM0_J']]
    logging.debug(f"CM0_J: {path_master['CM0_J']}")

    path_master['CM1_P'] = [sheet['B3'].value, sheet['C3'].value, sheet['D3'].value,
                            sheet['E3'].value, sheet['F3'].value, sheet['G3'].value]
    path_master['CM1_P'][0:3] = [x / 1000.0 for x in path_master['CM1_P'][0:3]]
    logging.debug(f"CM1_P: {path_master['CM1_P']}")

    path_master['CM1_J'] = [sheet['H3'].value, sheet['I3'].value, sheet['J3'].value,
                            sheet['K3'].value, sheet['L3'].value, sheet['M3'].value]
    path_master['CM1_J'] = [math.radians(x) for x in path_master['CM1_J']]
    logging.debug(f"CM1_J: {path_master['CM1_J']}")

    path_master['CM2_P'] = [sheet['B4'].value, sheet['C4'].value, sheet['D4'].value,
                            sheet['E4'].value, sheet['F4'].value, sheet['G4'].value]
    path_master['CM2_P'][0:3] = [x / 1000.0 for x in path_master['CM2_P'][0:3]]
    logging.debug(f"CM2_P: {path_master['CM2_P']}")

    path_master['CM2_J'] = [sheet['H4'].value, sheet['I4'].value, sheet['J4'].value,
                            sheet['K4'].value, sheet['L4'].value, sheet['M4'].value]
    path_master['CM2_J'] = [math.radians(x) for x in path_master['CM2_J']]
    logging.debug(f"CM2_J: {path_master['CM2_J']}")

    path_master['CM3_P'] = [sheet['B5'].value, sheet['C5'].value, sheet['D5'].value,
                            sheet['E5'].value, sheet['F5'].value, sheet['G5'].value]
    path_master['CM3_P'][0:3] = [x / 1000.0 for x in path_master['CM3_P'][0:3]]
    logging.debug(f"CM3_P: {path_master['CM3_P']}")

    path_master['CM3_J'] = [sheet['H5'].value, sheet['I5'].value, sheet['J5'].value,
                            sheet['K5'].value, sheet['L5'].value, sheet['M5'].value]
    path_master['CM3_J'] = [math.radians(x) for x in path_master['CM3_J']]
    logging.debug(f"CM3_J: {path_master['CM3_J']}")

    path_master['CM4_P'] = [sheet['B6'].value, sheet['C6'].value, sheet['D6'].value,
                            sheet['E6'].value, sheet['F6'].value, sheet['G6'].value]
    path_master['CM4_P'][0:3] = [x / 1000.0 for x in path_master['CM4_P'][0:3]]
    logging.debug(f"CM4_P: {path_master['CM4_P']}")

    path_master['CM4_J'] = [sheet['H6'].value, sheet['I6'].value, sheet['J6'].value,
                            sheet['K6'].value, sheet['L6'].value, sheet['M6'].value]
    path_master['CM4_J'] = [math.radians(x) for x in path_master['CM4_J']]
    logging.debug(f"CM4_J: {path_master['CM4_J']}")

    path_master['CM5_P'] = [sheet['B7'].value, sheet['C7'].value, sheet['D7'].value,
                            sheet['E7'].value, sheet['F7'].value, sheet['G7'].value]
    path_master['CM5_P'][0:3] = [x / 1000.0 for x in path_master['CM5_P'][0:3]]
    logging.debug(f"CM5_P: {path_master['CM5_P']}")

    path_master['CM5_J'] = [sheet['H7'].value, sheet['I7'].value, sheet['J7'].value,
                            sheet['K7'].value, sheet['L7'].value, sheet['M7'].value]
    path_master['CM5_J'] = [math.radians(x) for x in path_master['CM5_J']]
    logging.debug(f"CM5_J: {path_master['CM5_J']}")

    path_master['CM6_P'] = [sheet['B8'].value, sheet['C8'].value, sheet['D8'].value,
                            sheet['E8'].value, sheet['F8'].value, sheet['G8'].value]
    path_master['CM6_P'][0:3] = [x / 1000.0 for x in path_master['CM6_P'][0:3]]
    logging.debug(f"CM6_P: {path_master['CM6_P']}")

    path_master['CM6_J'] = [sheet['H8'].value, sheet['I8'].value, sheet['J8'].value,
                            sheet['K8'].value, sheet['L8'].value, sheet['M8'].value]
    path_master['CM6_J'] = [math.radians(x) for x in path_master['CM6_J']]
    logging.debug(f"CM6_J: {path_master['CM6_J']}")

    path_master['CM7_P'] = [sheet['B9'].value, sheet['C9'].value, sheet['D9'].value,
                            sheet['E9'].value, sheet['F9'].value, sheet['G9'].value]
    path_master['CM7_P'][0:3] = [x / 1000.0 for x in path_master['CM7_P'][0:3]]
    logging.debug(f"CM7_P: {path_master['CM7_P']}")

    path_master['CM7_J'] = [sheet['H9'].value, sheet['I9'].value, sheet['J9'].value,
                            sheet['K9'].value, sheet['L9'].value, sheet['M9'].value]
    path_master['CM7_J'] = [math.radians(x) for x in path_master['CM7_J']]
    logging.debug(f"CM7_J: {path_master['CM7_J']}")

    # TODO: add new master waypoints here
    # path_master['CM8_P'] = [sheet['B10'].value, sheet['C10'].value, sheet['D10'].value,
    #                         sheet['E10'].value, sheet['F10'].value, sheet['G10'].value]
    # path_master['CM8_P'][0:3] = [x / 1000.0 for x in path_master['CM8_P'][0:3]]
    # logging.debug(f"CM8_P: {path_master['CM8_P']}")
    #
    # path_master['CM8_J'] = [sheet['H10'].value, sheet['I10'].value, sheet['J10'].value,
    #                         sheet['K10'].value, sheet['L10'].value, sheet['M10'].value]
    # path_master['CM8_J'] = [math.radians(x) for x in path_master['CM8_J']]
    # logging.debug(f"CM8_J: {path_master['CM8_J']}")

    # Change the sheet
    sheet = wb[CONFIG_FILE_SHEET_SLAVE]

    path_slave['CS0_P'] = [sheet['B2'].value, sheet['C2'].value, sheet['D2'].value,
                           sheet['E2'].value, sheet['F2'].value, sheet['G2'].value]
    path_slave['CS0_P'][0:3] = [x / 1000.0 for x in path_slave['CS0_P'][0:3]]
    logging.debug(f"CS0_P: {path_slave['CS0_P']}")

    path_slave['CS0_J'] = [sheet['H2'].value, sheet['I2'].value, sheet['J2'].value,
                           sheet['K2'].value, sheet['L2'].value, sheet['M2'].value]
    path_slave['CS0_J'] = [math.radians(x) for x in path_slave['CS0_J']]
    logging.debug(f"CS0_J: {path_slave['CS0_J']}")

    path_slave['CS1_P'] = [sheet['B3'].value, sheet['C3'].value, sheet['D3'].value,
                           sheet['E3'].value, sheet['F3'].value, sheet['G3'].value]
    path_slave['CS1_P'][0:3] = [x / 1000.0 for x in path_slave['CS1_P'][0:3]]
    logging.debug(f"CS1_P: {path_slave['CS1_P']}")

    path_slave['CS1_J'] = [sheet['H3'].value, sheet['I3'].value, sheet['J3'].value,
                           sheet['K3'].value, sheet['L3'].value, sheet['M3'].value]
    path_slave['CS1_J'] = [math.radians(x) for x in path_slave['CS1_J']]
    logging.debug(f"CS1_J: {path_slave['CS1_J']}")

    path_slave['CS2_P'] = [sheet['B4'].value, sheet['C4'].value, sheet['D4'].value,
                           sheet['E4'].value, sheet['F4'].value, sheet['G4'].value]
    path_slave['CS2_P'][0:3] = [x / 1000.0 for x in path_slave['CS2_P'][0:3]]
    logging.debug(f"CS2_P: {path_slave['CS2_P']}")

    path_slave['CS2_J'] = [sheet['H4'].value, sheet['I4'].value, sheet['J4'].value,
                           sheet['K4'].value, sheet['L4'].value, sheet['M4'].value]
    path_slave['CS2_J'] = [math.radians(x) for x in path_slave['CS2_J']]
    logging.debug(f"CS2_J: {path_slave['CS2_J']}")

    path_slave['CS3_P'] = [sheet['B5'].value, sheet['C5'].value, sheet['D5'].value,
                           sheet['E5'].value, sheet['F5'].value, sheet['G5'].value]
    path_slave['CS3_P'][0:3] = [x / 1000.0 for x in path_slave['CS3_P'][0:3]]
    logging.debug(f"CS3_P: {path_slave['CS3_P']}")

    path_slave['CS3_J'] = [sheet['H5'].value, sheet['I5'].value, sheet['J5'].value,
                           sheet['K5'].value, sheet['L5'].value, sheet['M5'].value]
    path_slave['CS3_J'] = [math.radians(x) for x in path_slave['CS3_J']]
    logging.debug(f"CS3_J: {path_slave['CS3_J']}")

    path_slave['CS4_P'] = [sheet['B6'].value, sheet['C6'].value, sheet['D6'].value,
                           sheet['E6'].value, sheet['F6'].value, sheet['G6'].value]
    path_slave['CS4_P'][0:3] = [x / 1000.0 for x in path_slave['CS4_P'][0:3]]
    logging.debug(f"CS4_P: {path_slave['CS4_P']}")

    path_slave['CS4_J'] = [sheet['H6'].value, sheet['I6'].value, sheet['J6'].value,
                           sheet['K6'].value, sheet['L6'].value, sheet['M6'].value]
    path_slave['CS4_J'] = [math.radians(x) for x in path_slave['CS4_J']]
    logging.debug(f"CS4_J: {path_slave['CS4_J']}")

    path_slave['CS5_P'] = [sheet['B7'].value, sheet['C7'].value, sheet['D7'].value,
                           sheet['E7'].value, sheet['F7'].value, sheet['G7'].value]
    path_slave['CS5_P'][0:3] = [x / 1000.0 for x in path_slave['CS5_P'][0:3]]
    logging.debug(f"CS5_P: {path_slave['CS5_P']}")

    path_slave['CS5_J'] = [sheet['H7'].value, sheet['I7'].value, sheet['J7'].value,
                           sheet['K7'].value, sheet['L7'].value, sheet['M7'].value]
    path_slave['CS5_J'] = [math.radians(x) for x in path_slave['CS5_J']]
    logging.debug(f"CS5_J: {path_slave['CS5_J']}")

    # TODO: add new slave waypoints here
    path_slave['CS6_P'] = [sheet['B8'].value, sheet['C8'].value, sheet['D8'].value,
                           sheet['E8'].value, sheet['F8'].value, sheet['G8'].value]
    path_slave['CS6_P'][0:3] = [x / 1000.0 for x in path_slave['CS6_P'][0:3]]
    logging.debug(f"CS6_P: {path_slave['CS6_P']}")

    path_slave['CS6_J'] = [sheet['H8'].value, sheet['I8'].value, sheet['J8'].value,
                           sheet['K8'].value, sheet['L8'].value, sheet['M8'].value]
    path_slave['CS6_J'] = [math.radians(x) for x in path_slave['CS6_J']]
    logging.debug(f"CS6_J: {path_slave['CS6_J']}")

    path_slave['CS7_P'] = [sheet['B9'].value, sheet['C9'].value, sheet['D9'].value,
                           sheet['E9'].value, sheet['F9'].value, sheet['G9'].value]
    path_slave['CS7_P'][0:3] = [x / 1000.0 for x in path_slave['CS7_P'][0:3]]
    logging.debug(f"CS7_P: {path_slave['CS7_P']}")

    path_slave['CS7_J'] = [sheet['H9'].value, sheet['I9'].value, sheet['J9'].value,
                           sheet['K9'].value, sheet['L9'].value, sheet['M9'].value]
    path_slave['CS7_J'] = [math.radians(x) for x in path_slave['CS7_J']]
    logging.debug(f"CS7_J: {path_slave['CS7_J']}")

    return path_master, path_slave


def master_jogging_wait():
    if Config.JOGGING_ENABLE:
        logging.debug("Master-Fred: Press 'f' to continue")

        jogging_event['Master'].clear()
        jogging_event['Master'].wait()


def slave_jogging_wait():
    if Config.JOGGING_ENABLE:
        logging.debug("Slave-Erik: Press 'e' to continue")

        jogging_event['Slave'].clear()
        jogging_event['Slave'].wait()


def master_operate_gripper(target_width):
    # https://github.com/gouxiangchen/UR5-control-with-RG2/blob/master/test_main.py

    if target_width < 10 or target_width > 110:
        logging.debug('Gripper width out of bounds')
        return

    port = 30001
    host = Config.MASTER_IP
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((host, port))

    tcp_command = "def rg2ProgOpen():\n"
    tcp_command += "\ttextmsg(\"inside RG2 function called\")\n"

    tcp_command += '\ttarget_width={}\n'.format(target_width)
    tcp_command += "\ttarget_force=40\n"
    tcp_command += "\tpayload=1.0\n"
    tcp_command += "\tset_payload1=False\n"
    tcp_command += "\tdepth_compensation=False\n"
    tcp_command += "\tslave=False\n"

    tcp_command += "\ttimeout = 0\n"
    tcp_command += "\twhile get_digital_in(9) == False:\n"
    tcp_command += "\t\ttextmsg(\"inside while\")\n"
    tcp_command += "\t\tif timeout > 400:\n"
    tcp_command += "\t\t\tbreak\n"
    tcp_command += "\t\tend\n"
    tcp_command += "\t\ttimeout = timeout+1\n"
    tcp_command += "\t\tsync()\n"
    tcp_command += "\tend\n"
    tcp_command += "\ttextmsg(\"outside while\")\n"

    tcp_command += "\tdef bit(input):\n"
    tcp_command += "\t\tmsb=65536\n"
    tcp_command += "\t\tlocal i=0\n"
    tcp_command += "\t\tlocal output=0\n"
    tcp_command += "\t\twhile i<17:\n"
    tcp_command += "\t\t\tset_digital_out(8,True)\n"
    tcp_command += "\t\t\tif input>=msb:\n"
    tcp_command += "\t\t\t\tinput=input-msb\n"
    tcp_command += "\t\t\t\tset_digital_out(9,False)\n"
    tcp_command += "\t\t\telse:\n"
    tcp_command += "\t\t\t\tset_digital_out(9,True)\n"
    tcp_command += "\t\t\tend\n"
    tcp_command += "\t\t\tif get_digital_in(8):\n"
    tcp_command += "\t\t\t\tout=1\n"
    tcp_command += "\t\t\tend\n"
    tcp_command += "\t\t\tsync()\n"
    tcp_command += "\t\t\tset_digital_out(8,False)\n"
    tcp_command += "\t\t\tsync()\n"
    tcp_command += "\t\t\tinput=input*2\n"
    tcp_command += "\t\t\toutput=output*2\n"
    tcp_command += "\t\t\ti=i+1\n"
    tcp_command += "\t\tend\n"
    tcp_command += "\t\treturn output\n"
    tcp_command += "\tend\n"
    tcp_command += "\ttextmsg(\"outside bit definition\")\n"

    tcp_command += "\ttarget_width=target_width+0.0\n"
    tcp_command += "\tif target_force>40:\n"
    tcp_command += "\t\ttarget_force=40\n"
    tcp_command += "\tend\n"

    tcp_command += "\tif target_force<4:\n"
    tcp_command += "\t\ttarget_force=4\n"
    tcp_command += "\tend\n"
    tcp_command += "\tif target_width>110:\n"
    tcp_command += "\t\ttarget_width=110\n"
    tcp_command += "\tend\n"
    tcp_command += "\tif target_width<0:\n"
    tcp_command += "\t\ttarget_width=0\n"
    tcp_command += "\tend\n"
    tcp_command += "\trg_data=floor(target_width)*4\n"
    tcp_command += "\trg_data=rg_data+floor(target_force/2)*4*111\n"
    tcp_command += "\tif slave:\n"
    tcp_command += "\t\trg_data=rg_data+16384\n"
    tcp_command += "\tend\n"

    tcp_command += "\ttextmsg(\"about to call bit\")\n"
    tcp_command += "\tbit(rg_data)\n"
    tcp_command += "\ttextmsg(\"called bit\")\n"

    tcp_command += "\tif depth_compensation:\n"
    tcp_command += "\t\tfinger_length = 55.0/1000\n"
    tcp_command += "\t\tfinger_heigth_disp = 5.0/1000\n"
    tcp_command += "\t\tcenter_displacement = 7.5/1000\n"

    tcp_command += "\t\tstart_pose = get_forward_kin()\n"
    tcp_command += "\t\tset_analog_inputrange(2, 1)\n"
    tcp_command += "\t\tzscale = (get_analog_in(2)-0.026)/2.976\n"
    tcp_command += "\t\tzangle = zscale*1.57079633-0.087266462\n"
    tcp_command += "\t\tzwidth = 5+110*sin(zangle)\n"

    tcp_command += "\t\tstart_depth = cos(zangle)*finger_length\n"

    tcp_command += "\t\tsync()\n"
    tcp_command += "\t\tsync()\n"
    tcp_command += "\t\ttimeout = 0\n"

    tcp_command += "\t\twhile get_digital_in(9) == True:\n"
    tcp_command += "\t\t\ttimeout=timeout+1\n"
    tcp_command += "\t\t\tsync()\n"
    tcp_command += "\t\t\tif timeout > 20:\n"
    tcp_command += "\t\t\t\tbreak\n"
    tcp_command += "\t\t\tend\n"
    tcp_command += "\t\tend\n"
    tcp_command += "\t\ttimeout = 0\n"
    tcp_command += "\t\twhile get_digital_in(9) == False:\n"
    tcp_command += "\t\t\tzscale = (get_analog_in(2)-0.026)/2.976\n"
    tcp_command += "\t\t\tzangle = zscale*1.57079633-0.087266462\n"
    tcp_command += "\t\t\tzwidth = 5+110*sin(zangle)\n"
    tcp_command += "\t\t\tmeasure_depth = cos(zangle)*finger_length\n"
    tcp_command += "\t\t\tcompensation_depth = (measure_depth - start_depth)\n"
    tcp_command += "\t\t\ttarget_pose = pose_trans(start_pose,p[0,0,-compensation_depth,0,0,0])\n"
    tcp_command += "\t\t\tif timeout > 400:\n"
    tcp_command += "\t\t\t\tbreak\n"
    tcp_command += "\t\t\tend\n"
    tcp_command += "\t\t\ttimeout=timeout+1\n"
    tcp_command += "\t\t\tservoj(get_inverse_kin(target_pose),0,0,0.008,0.033,1700)\n"
    tcp_command += "\t\tend\n"
    tcp_command += "\t\tnspeed = norm(get_actual_tcp_speed())\n"
    tcp_command += "\t\twhile nspeed > 0.001:\n"
    tcp_command += "\t\t\tservoj(get_inverse_kin(target_pose),0,0,0.008,0.033,1700)\n"
    tcp_command += "\t\t\tnspeed = norm(get_actual_tcp_speed())\n"
    tcp_command += "\t\tend\n"
    tcp_command += "\tend\n"
    tcp_command += "\tif depth_compensation==False:\n"
    tcp_command += "\t\ttimeout = 0\n"
    tcp_command += "\t\twhile get_digital_in(9) == True:\n"
    tcp_command += "\t\t\ttimeout = timeout+1\n"
    tcp_command += "\t\t\tsync()\n"
    tcp_command += "\t\t\tif timeout > 20:\n"
    tcp_command += "\t\t\t\tbreak\n"
    tcp_command += "\t\t\tend\n"
    tcp_command += "\t\tend\n"
    tcp_command += "\t\ttimeout = 0\n"
    tcp_command += "\t\twhile get_digital_in(9) == False:\n"
    tcp_command += "\t\t\ttimeout = timeout+1\n"
    tcp_command += "\t\t\tsync()\n"
    tcp_command += "\t\t\tif timeout > 400:\n"
    tcp_command += "\t\t\t\tbreak\n"
    tcp_command += "\t\t\tend\n"
    tcp_command += "\t\tend\n"
    tcp_command += "\tend\n"
    tcp_command += "\tif set_payload1:\n"
    tcp_command += "\t\tif slave:\n"
    tcp_command += "\t\t\tif get_analog_in(3) < 2:\n"
    tcp_command += "\t\t\t\tzslam=0\n"
    tcp_command += "\t\t\telse:\n"
    tcp_command += "\t\t\t\tzslam=payload\n"
    tcp_command += "\t\t\tend\n"
    tcp_command += "\t\telse:\n"
    tcp_command += "\t\t\tif get_digital_in(8) == False:\n"
    tcp_command += "\t\t\t\tzmasm=0\n"
    tcp_command += "\t\t\telse:\n"
    tcp_command += "\t\t\t\tzmasm=payload\n"
    tcp_command += "\t\t\tend\n"
    tcp_command += "\t\tend\n"
    tcp_command += "\t\tzsysm=0.0\n"
    tcp_command += "\t\tzload=zmasm+zslam+zsysm\n"
    tcp_command += "\t\tset_payload(zload)\n"
    tcp_command += "\tend\n"

    tcp_command += "end\n"

    tcp_socket.send(str.encode(tcp_command))
    tcp_socket.close()
    time.sleep(1)


def master_gripper_toggle(state='Open'):
    logging.info(f'Master RG2 gripper state: {state} ')
    # This function accepts either 'Open' or 'Close'

    if state == 'Open':
        master_operate_gripper(Config.MASTER_GRIPPER_WIDTH_OPENED)

    elif state == 'Close':
        master_operate_gripper(Config.MASTER_GRIPPER_WIDTH_CLOSED)

    else:
        logging.info('Invalid gripper option given')
        return


def master_connect():
    try:
        robot = rtde_control.RTDEControlInterface(Config.MASTER_IP)

    except:
        text = f"Cannot connect to robot at: {Config.MASTER_IP}"

        logging.info(text)
        exit(text)

    logging.info(f"Connected to robot at: {Config.MASTER_IP}")

    # robot.setPayload(1, (0, 0, 0.01))
    return robot


def slave_connect():
    try:
        robot = rtde_control.RTDEControlInterface(Config.SLAVE_IP)

    except:
        text = f"Cannot connect to robot at: {Config.SLAVE_IP}"

        logging.info(text)
        exit(text)

    logging.info(f"Connected to robot at: {Config.SLAVE_IP}")

    # robot.setPayload(1, (0, 0, 0.01))
    return robot


def master_disconnect(robot):
    robot.disconnect()
    logging.info('Disconnected master robot')
    # time.sleep(1)


def slave_disconnect(robot):
    robot.disconnect()
    logging.info('Disconnected master robot')
    # time.sleep(1)


def slave_gripper_toggle(state='Open'):
    logging.info(f'Slave RG2-FT gripper state: {state} ')
    # This function accepts either 'Open' or 'Close'

    ip = Config.SLAVE_GRIPPER_IP

    if state == 'Open':
        width = Config.SLAVE_GRIPPER_WIDTH_OPENED

    elif state == 'Close':
        width = Config.SLAVE_GRIPPER_WIDTH_CLOSED
    else:
        # log error
        logging.info('Invalid gripper option given')
        return

    curl_text = f'http://{ip}/api/dc/rg2ft/set_width/{width}/40'
    logging.debug(f"Sending command to gripper: {curl_text}")
    requests.get(curl_text)

    time.sleep(1)


def master_movel_time_based(pose, a=1, v=0.06, t=2):
    message = f"movel(p{pose}, a={a}, v={v}, t={t}, r=0)\n"
    logging.info(f'Time-based movel: {message}')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((Config.MASTER_IP, 30001))

    s.send(str.encode(message))
    s.close()
    time.sleep(t + 0.05)
    return


def slave_movel_time_based(pose, a=1, v=0.06, t=2):
    message = f"movel(p{pose}, a={a}, v={v}, t={t}, r=0)\n"
    logging.info(f'Time-based movel: {message}')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((Config.SLAVE_IP, 30001))

    s.send(str.encode(message))
    s.close()
    time.sleep(t + 0.05)
    return


def master_thread(sync_event, path):
    logging.info(f'Starting master')

    robot = master_connect()

    # master_movel_time_based(pose=path['CM5_P'], t=5)

    sync_event['Master'].clear()

    master_disconnect(robot)
    master_gripper_toggle('Open')
    robot = master_connect()

    master_jogging_wait()
    robot.moveJ(path['CM1_J'], j_speed, j_acc)
    logging.info(f'CM1: M Start Up')

    # master_jogging_wait()
    # robot.moveL(path['CM8_P'], j_speed, j_acc)
    # logging.info(f'CM8')

    master_disconnect(robot)
    master_gripper_toggle('Open')
    robot = master_connect()

    master_jogging_wait()
    robot.moveL(path['CM2_P'], l_speed, l_acc)
    logging.info(f'CM2: M Start Down')

    master_disconnect(robot)
    master_gripper_toggle('Close')
    robot = master_connect()

    master_jogging_wait()
    robot.moveL(path['CM1_P'], l_speed, l_acc)
    logging.info(f'CM1: M Start Up')

    master_jogging_wait()
    robot.moveJ(path['CM3_J'], j_speed, j_acc)
    logging.info(f'CM3: M Start Oriented')

    master_jogging_wait()
    robot.moveJ(path['CM4_J'], j_speed, j_acc)
    logging.info(f'CM4: M Sync Begin')

    if Config.SLAVE_ENABLE:
        sync_event['Master'].set()
        logging.info('Signaling to slave')

        logging.debug('Waiting for slave')
        sync_event['Slave'].wait()
        sync_event['Slave'].clear()

    # time.sleep(0.1)

    master_jogging_wait()
    robot.moveL(path['CM5_P'], l_speed * 0.64, l_acc)
    # master_disconnect(robot)
    # master_movel_time_based(pose=path['CM5_P'], t=3)
    # robot = master_connect()
    logging.info(f'CM5: M Sync End')

    # ez csak tesztre
    # master_jogging_wait()
    # # robot.moveL(path['CM4_P'], l_speed, l_acc)
    # master_disconnect(robot)
    # master_movel_time_based(pose=path['CM4_P'], t=5)
    # logging.info(f'CM4: M Sync Begin')
    # robot = master_connect()
    # return

    if Config.SLAVE_ENABLE:
        logging.debug('Waiting for slave')

        sync_event['Slave'].wait()
        sync_event['Slave'].clear()

    master_jogging_wait()
    robot.moveJ(path['CM6_J'], j_speed, j_acc)
    logging.info(f'CM6: M Goal Up')

    master_jogging_wait()
    robot.moveL(path['CM7_P'], l_speed, l_acc)
    logging.info(f'CM7: M Goal Down')

    master_disconnect(robot)
    master_gripper_toggle('Open')
    robot = master_connect()

    master_jogging_wait()
    robot.moveL(path['CM6_P'], l_speed, l_acc)
    logging.info(f'CM6: M Goal Up')

    master_disconnect(robot)
    master_gripper_toggle('Close')
    robot = master_connect()

    master_jogging_wait()
    robot.moveL(path['CM1_P'], l_speed, l_acc)
    logging.info(f'CM1: M Start Up')

    # Stop the control script
    robot.stopScript()

    logging.info('Done')


def slave_thread(sync_event, path):
    logging.info(f'Starting slave')

    robot = slave_connect()

    sync_event['Slave'].clear()

    slave_gripper_toggle('Open')

    slave_jogging_wait()
    robot.moveJ(path['CS1_J'], j_speed, j_acc)
    logging.info(f'CS1: S Start Up')

    slave_jogging_wait()
    robot.moveL(path['CS2_P'], l_speed, l_acc)
    logging.info(f'CS2: S Start Down')

    slave_gripper_toggle('Close')

    slave_jogging_wait()
    robot.moveL(path['CS1_P'], l_speed, l_acc)
    logging.info(f'CS1: S Start Up')

    slave_jogging_wait()
    robot.moveJ(path['CS3_J'], j_speed, j_acc)
    logging.info(f'CS3: S Start Oriented')

    slave_jogging_wait()
    robot.moveJ(path['CS4_J'], j_speed, j_acc)
    logging.info(f'CS4: S Sync Begin')

    time.sleep(0.5)

    if Config.MASTER_ENABLE:
        logging.debug('Waiting for master')

        sync_event['Master'].wait()
        sync_event['Master'].clear()

    slave_jogging_wait()
    robot.moveL(path['CS5_P'], l_speed, l_acc)
    # robot.disconnect()
    # slave_movel_time_based(pose=path['CS5_P'], t=3)
    # robot = slave_connect()
    logging.info(f'CS5: S Sync End')

    if Config.MASTER_ENABLE:
        sync_event['Slave'].set()
        logging.debug('Signaling to master')

    # time.sleep(0.09)

    slave_jogging_wait()
    robot.moveL(path['CS6_P'], l_speed, l_acc)
    logging.info(f'CS6: S Sync Begin Rotated')

    # slave_jogging_wait()
    # robot.moveL(path['CS4_P'], l_speed, l_acc)
    # # robot.disconnect()
    # # slave_movel_time_based(pose=path['CS4_P'], t=3)
    # # robot = slave_connect()
    # logging.info(f'CS4: S Sync Begin')

    # slave_jogging_wait()
    # robot.moveJ(path['CS6_J'], j_speed, j_acc)
    # # # # robot.disconnect()
    # # # # slave_movel_time_based(pose=path['CS6_P'], t=8)
    # # # # robot = slave_connect()
    # logging.info(f'CS6: S Sync Begin Rotated')

    slave_gripper_toggle('Open')

    slave_jogging_wait()
    robot.moveL(path['CS7_P'], l_speed, l_acc)
    logging.info(f'CS7: S Sync Retreat')

    slave_jogging_wait()
    robot.moveJ(path['CS3_J'], j_speed, j_acc)
    logging.info(f'CS3: S Start Oriented')

    if Config.MASTER_ENABLE:
        sync_event['Slave'].set()
        logging.debug('Signaling to master')

    # slave_jogging_wait()
    # # robot.moveL(path['CS6_P'], l_speed, l_acc)
    # robot.disconnect()
    # slave_movel_time_based(pose=path['CS6_P'], t=8)
    # robot = slave_connect()
    # logging.info(f'CS6: S Sync Begin Rotated')

    # csak mikor nemkell forgas

    # ez csak teszt
    # slave_jogging_wait()
    # robot.moveL(path['CS4_P'], l_speed, l_acc)
    # logging.info(f'CS4: S Sync Begin')
    # return

    slave_jogging_wait()
    robot.moveJ(path['CS1_J'], j_speed, j_acc)
    logging.info(f'CS1: S Start Up')

    # Stop the control script
    robot.stopScript()

    logging.info('Done')


class RemoteFuncs:
    def signalMaster(self):
        # jogging_wait['Master'] = True
        jogging_event['Master'].set()
        return 0

    def signalSlave(self):
        # jogging_wait['Slave'] = True
        jogging_event['Slave'].set()
        return 0


class ServerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.localServer = SimpleXMLRPCServer(('0.0.0.0', 8888))
        self.localServer.register_instance(RemoteFuncs())

    def run(self):
        self.localServer.serve_forever()


if __name__ == '__main__':
    logging.config.fileConfig(os.path.join(SCRIPT_DIR, 'log_config.ini'))

    if Config.EXECUTION == 'SLOW':
        j_speed = Config.J_SPEED_SLOW
        l_speed = Config.L_SPEED_SLOW

        j_acc = Config.J_ACC_SLOW
        l_acc = Config.L_ACC_SLOW

        logging.info("Execution speed: slow")

    elif Config.EXECUTION == 'FAST':
        j_speed = Config.J_SPEED_FAST
        l_speed = Config.L_SPEED_FAST

        j_acc = Config.J_ACC_FAST
        l_acc = Config.L_ACC_FAST

        logging.info("Execution speed: fast")

    if Config.JOGGING_ENABLE:
        logging.info('Jogging enabled')

    # TODO: eliminate excel
    # Reads from m and s sheets
    path_master, path_slave = read_path_waypoints_from_file()
    # write_paths_to_json(path_master, path_slave)

    # TODO: Prefer this
    # path_master, path_slave = read_paths_from_json()

    sync_event = {
        'Master': threading.Event(),
        'Slave': threading.Event()
    }

    logging.info('Spawning XMLRPC listener thread')
    xmlrpcServer = ServerThread()
    xmlrpcServer.start()

    if Config.MASTER_ENABLE:
        master_thread = threading.Thread(name='MasterThread', target=master_thread, args=(sync_event, path_master))
        master_thread.start()

    if Config.SLAVE_ENABLE:
        slave_thread = threading.Thread(name='SlaveThread', target=slave_thread, args=(sync_event, path_slave))
        slave_thread.start()

    if Config.MASTER_ENABLE:
        master_thread.join()

    if Config.SLAVE_ENABLE:
        slave_thread.join()

    logging.info("Done")
