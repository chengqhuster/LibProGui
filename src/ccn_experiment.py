# encoding=utf-8

import serial
import time
import schedule
import random
import threading
import logging

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

CONENT_DIC = {0: 'tempr',
              1: 'marat'}

REQ_STATE = bytearray(10)
REVC_STATE = bytearray(10)

TIME_STAMP = list(range(len(REQ_STATE)))


def interest_req(index, ser):
    global REVC_STATE
    global TIME_STAMP
    REVC_STATE[index] = 1
    target = str(index % 5 + 2)
    content = 1 if index > 4 else 0
    name = 'dev0' + target + '/' + CONENT_DIC[content]
    for i in range(3):
        if REVC_STATE[index] == 0:
            return
        else:
            logger.info("Reqest content {}, try time {}".format(name, i + 1))
            REVC_STATE[index] = i + 1
            recv_core.send_req(recv_core.REMOT_TYPE,
                               target,
                               '3',
                               CONENT_DIC[content] + str((index + 2) * 600),
                               ser)
            TIME_STAMP[index] = round(time.time() * 1000)
            time.sleep(2)


def recv_ack(ser):
    global REVC_STATE
    global TIME_STAMP
    while True:
        frame, recvlen = serialComm.pppread(ser, 1024)
        print(frame[0:recvlen])
        if frame[6] == 1:
            name = recv_core.getstr(frame[7: 27])
            target = int(name[4]) - 2
            if name[6:] == 'marat':
                target += 5
            if REVC_STATE[target] > 0:
                REVC_STATE[target] = 0
                ct = round(time.time() * 1000)
                req_delay = ct - TIME_STAMP[target]
                gtime = frame[73] + (frame[74] << 8) + (frame[75] << 16) + (frame[76] << 24)
                messega = "Return content {} info,\tisCachedCopy {}\thops {}\t " \
                          "contentGeneratedTime {}\treqDelay {}\t"\
                    .format(name, frame[69], frame[70], gtime, req_delay)
                logger.info(messega)
                frame[6] = 0xff
                frame[27] = 0xff
                serialComm.pppsend(ser, frame[4: 30])


def choose_req(ser):
    global REQ_STATE
    if REQ_STATE.count(0) == 0:
        REQ_STATE = bytearray(10)
    # 顺序请求
    for i in range(len(REQ_STATE)):
        if REQ_STATE[i] == 0:
            REQ_STATE[i] = 1
            req_thread = threading.Thread(target=interest_req, args=(i, ser,), name='req_thread')
            req_thread.start()
            break
    # left = REQ_STATE.count(0)
    # if left == 0:
    #     REQ_STATE = bytearray(10)
    #     left = len(REQ_STATE)
    # choose = random.randint(1, left)
    # for i in range(len(REQ_STATE)):
    #     if REQ_STATE[i] == 0:
    #         choose -= 1
    #         if choose == 0:
    #             REQ_STATE[i] = 1
    #             req_thread = threading.Thread(target=interest_req, args=(i, ser,), name='req_thread')
    #             req_thread.start()
    #             break


if __name__ == '__main__':
    # logger config
    logger = logging.getLogger('ccn_experiment')
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler('../log/12-19 07.28 MyCache experiment.log')
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    # dev01作为网关节点
    recv_core.connection_init()
    se = serial.Serial()
    try:
        logger.info('Connection to ' + recv_core.COM + '......')
        se = serial.Serial(recv_core.COM, 115200)
        logger.info('Connection Success\n')
    except serial.serialutil.SerialException as ex:
        logger.error(ex)

    recv_core.connect_try(se)

    recv_thread = threading.Thread(target=recv_ack, args=(se,), name='recv_thread')
    recv_thread.start()

    schedule.every(6).seconds.do(choose_req, se)
    while True:
        schedule.run_pending()
        time.sleep(1)

