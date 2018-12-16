import serial
import time

import serialComm
import recv_core

# 设备列表
DEV00_NAME = b'dev00'
DEV00_MAC = b'\xf4\xb8\x5e\xcb\xb0\x22'
DEV01_NAME = b'dev01'
DEV01_MAC = b'\xf4\xb8\x5e\xcb\xad\x64'
DEV02_NAME = b'dev02'
DEV02_MAC = b'\xc4\xbe\x84\xe8\x69\xcb'
DEV03_NAME = b'dev03'
DEV03_MAC = b'\xf4\xb8\x5e\xcb\x86\x65'
DEV04_NAME = b'dev04'
DEV04_MAC = b'\xc4\xbe\x84\x74\x20\x82'
DEV05_NAME = b'dev05'
DEV05_MAC = b'\xd4\xf5\x13\x04\x03\x15'
DEV06_NAME = b'dev06'
DEV06_MAC = b'\xc4\xbe\x84\xf1\xad\xb1'
DEVICE_DICT = {DEV00_NAME: DEV00_MAC,
               DEV01_NAME: DEV01_MAC,
               DEV02_NAME: DEV02_MAC,
               DEV03_NAME: DEV03_MAC,
               DEV04_NAME: DEV04_MAC,
               DEV05_NAME: DEV05_MAC,
               DEV06_NAME: DEV06_MAC}

# DEV07_NAME = b'dev07'
# DEV07_MAC = b'\xff\xff\xff\xff\xff\xff'

if __name__ == '__main__':
    recv_core.connection_init()
    se = serial.Serial()
    try:
        print('Connection to ' + recv_core.COM + '......')
        se = serial.Serial(recv_core.COM, 115200)
        print('Connection Success\n')
    except serial.serialutil.SerialException as ex:
        print(ex)
    recv_core.connect_try(se)
    # dev01作为网关节点
    while True:
        recv_core.send_req(recv_core.CTROL_TYPE,
                           recv_core.CTROL_NEFBD,
                           recv_core.CTROL_NEFBD_ADD,
                           DEV02_MAC, se)
        frame, recvlen = serialComm.pppread(se, 1024)
        print(frame[0: recvlen])
        if frame[7: 27] == recv_core.DEVICE_CRTOL and (frame[27] == 0 or frame[27] == 1):
            break
        else:
            time.sleep(2)
    while True:
        recv_core.send_req(recv_core.CTROL_TYPE,
                           recv_core.CTROL_NEFBD,
                           recv_core.CTROL_NEFBD_ADD,
                           DEV03_MAC, se)
        frame, recvlen = serialComm.pppread(se, 1024)
        print(frame[0: recvlen])
        if frame[7: 27] == recv_core.DEVICE_CRTOL and (frame[27] == 0 or frame[27] == 1):
            break
        else:
            time.sleep(2)
    # recv_core.readfxn(se)
