import serial
import serial.tools.list_ports as lport
import logging
import threading

import serialComm
import ccn_experiment

# logging.basicConfig(level=logging.ERROR)
# log = logging.getLogger(__name__)
# log.propagate = False

COM = "COM"
NAME = b'12345'

CTROL = b'/ctrol\x00\x00\x00\x00\x00\x00\x00\x00\x00'
INFOM = b'/infom\x00\x00\x00\x00\x00\x00\x00\x00\x00'
TEMPR = b'/tempr\x00\x00\x00\x00\x00\x00\x00\x00\x00'

DEVICE_INFOM = NAME + INFOM
DEVICE_CRTOL = NAME + CTROL
DEVICE_TEMPR = NAME + TEMPR

INFOM_PREFIX = bytearray(b'\x00\x00\x01' + DEVICE_INFOM)
CTROL_PREDIX = bytearray(b'\x00\x00\x01' + DEVICE_CRTOL)
TEMPR_PREFIX = bytearray(b'\x00\x00\x01' + DEVICE_TEMPR)

TYPE_LOCATION = 24
CTROL_TYPE = '1'
INFOM_TYPE = '2'
TEMPR_TYPE = '3'
REMOT_TYPE = '4'


def type_introduct():
    print('\nPlease choose your request type')
    while True:
        print(CTROL_TYPE + ' : ctrol_type')
        print(INFOM_TYPE + ' : infom_type')
        print(TEMPR_TYPE + ' : tempr_type')
        print(REMOT_TYPE + ' : remote_type')
        numstr = input()
        if numstr == CTROL_TYPE:
            return CTROL_TYPE
        elif numstr == INFOM_TYPE:
            return INFOM_TYPE
        elif numstr == TEMPR_TYPE:
            return TEMPR_TYPE
        elif numstr == REMOT_TYPE:
            return REMOT_TYPE
        else:
            print('\nInvalid input, please choose again')

INFOM_NEIGH = '0'
INFOM_CONTE = '1'
INFOM_FIBLT = '2'
INFOM_DEVIS = '3'
INFOM_PITLT = '4'
INFOM_LTIME = '5'
INFOM_CACHE = '6'


def infom_choose():
    print('\nPlease choose your infom request type')
    while True:
        print(INFOM_NEIGH + ' : 邻居表')
        print(INFOM_CONTE + ' : 内容表')
        print(INFOM_FIBLT + ' : FIB表')
        print(INFOM_DEVIS + ' : 设备信息')
        print(INFOM_PITLT + ' : PIT表')
        print(INFOM_LTIME + ' : 本地时间')
        print(INFOM_CACHE + ' : 缓存信息')
        numstr = input()
        if numstr == INFOM_NEIGH:
            return INFOM_NEIGH
        elif numstr == INFOM_CONTE:
            return INFOM_CONTE
        elif numstr == INFOM_FIBLT:
            return INFOM_FIBLT
        elif numstr == INFOM_DEVIS:
            return INFOM_DEVIS
        elif numstr == INFOM_PITLT:
            return INFOM_PITLT
        elif numstr == INFOM_LTIME:
            return INFOM_LTIME
        elif numstr == INFOM_CACHE:
            return INFOM_CACHE
        else:
            print('\nInvalid input, please choose again')

CTROL_NEFBD = '0'
CTROL_NEFBD_ADD = '0'
CTROL_NEFBD_DEL = '1'
# CTROL_CSREG = '1'
# CTROL_FIBLT = '2'
CTROL_CHANG = '3'
CTROL_LEDON = '4'
CTROL_TIMEX = '5'


def ctrol_choose():
    print('\nPlease choose your ctrol request type')
    while True:
        print(CTROL_NEFBD + ' : 禁止表')
        print(CTROL_CHANG + ' : 设备信息')
        print(CTROL_LEDON + ' : LED')
        print(CTROL_TIMEX + ' : 激活时间')
        numstr = input()
        if numstr == CTROL_NEFBD:
            print('\nPlease choose your neighbour forbid action')
            while True:
                print(CTROL_NEFBD_ADD + ' : 添加禁止邻居')
                print(CTROL_NEFBD_DEL + ' : 删除禁止邻居')
                param = input()
                if param == CTROL_NEFBD_ADD or param == CTROL_NEFBD_DEL:
                    break
                else:
                    print('\nInvalid input, please choose again')
            print('\nPlease input forbid mac[0-6]')
            pa = input()
            return CTROL_NEFBD, param, pa
        elif numstr == CTROL_CHANG:
            print('\nPlease input device name')
            pa = input().encode('ascii')
            return CTROL_CHANG, None, pa
        elif numstr == CTROL_LEDON:
            while True:
                print('\nPlease input LED on time')
                param = input()
            return CTROL_LEDON, param, None
        elif numstr == CTROL_TIMEX:
            return CTROL_TIMEX, None, None
        else:
            print('\nInvalid input, please choose again')


def connection_init():
    global COM
    portlist = lport.comports()
    for port in portlist:
        print(port)
    while True:
        print('Please input com port num')
        comstr = input()
        try:
            int(comstr)
            COM += comstr
            break
        except ValueError:
            print('Your input is invalid')


def connect_try(ser):
    global NAME
    global DEVICE_CRTOL
    global DEVICE_INFOM
    global DEVICE_TEMPR
    global INFOM_PREFIX
    global CTROL_PREDIX
    global TEMPR_PREFIX
    connect_success = b'ReqForAConnection_OK'
    send = bytearray(b'\x00\x00\x01ReqForAConnection\x00\x00\x00')
    serialComm.pppsend(ser, send)
    recmessage = serialComm.pppread(ser, 1024)
    if recmessage[0][6] == 0xff and recmessage[0][7:27] == connect_success:
        NAME = recmessage[0][27:32]
        mac = recmessage[0][32:38]
        DEVICE_CRTOL = NAME + CTROL
        DEVICE_INFOM = NAME + INFOM
        DEVICE_TEMPR = NAME + TEMPR
        INFOM_PREFIX = bytearray(b'\x00\x00\x01' + DEVICE_INFOM)
        CTROL_PREDIX = bytearray(b'\x00\x00\x01' + DEVICE_CRTOL)
        TEMPR_PREFIX = bytearray(b'\x00\x00\x01' + DEVICE_TEMPR)
        print('Device Name: ' + getstr(NAME))
        print('Device Mac Addr: ', end='')
        for mac_byte in mac:
            print(' {:0>2x}'.format(mac_byte), end='')
        print('\n')


def getstr(frameblock):
    validnum = 0
    for letter in frameblock:
        if letter == 0x00:
            break
        else:
            validnum += 1
    return str(frameblock[0:validnum], encoding='ascii')


def choose_fxn(ser):
    while True:
        req_type = type_introduct()
        if req_type == CTROL_TYPE:
            ctrol_type, param, pa = ctrol_choose()
            send_req(CTROL_TYPE, ctrol_type, param, pa, ser)
        elif req_type == INFOM_TYPE:
            infom_type = infom_choose()
            send_req(INFOM_TYPE, infom_type, None, None, ser)
        elif req_type == TEMPR_TYPE:
            send_req(TEMPR_TYPE, None, None, None, ser)
        elif req_type == REMOT_TYPE:
            while True:
                print('Choose target device[0-6]')
                target_num = int(input())
                if 0 <= target_num <= 6:
                    break
                else:
                    print('Your input is invalid')
            while True:
                print('1' + ' : 添加邻居禁止')
                print('2' + ' : 点亮LED')
                print('3' + ' : 请求内容')
                action_num = input()
                if action_num == '1':
                    while True:
                        print('Please input forbidden device[0-6]')
                        forbid_device = int(input())
                        if 0 <= forbid_device <= 6:
                            break
                        else:
                            print('Your input is invalid')
                    send_req(REMOT_TYPE, target_num, action_num, forbid_device, ser)
                    break
                elif action_num == '2':
                    print('Please input LED last time')
                    last_time = input()
                    send_req(REMOT_TYPE, target_num, action_num, last_time, ser)
                    break
                elif action_num == '3':
                    print('Please input content name')
                    content = input()
                    send_req(REMOT_TYPE, target_num, action_num, content, ser)
                    break


def send_req(req_type, parmas_a, parmas_b, pa, ser):
    if req_type == INFOM_TYPE:
        send = INFOM_PREFIX + bytearray(2)
        num = int(parmas_a)
        send[TYPE_LOCATION] = num
    elif req_type == CTROL_TYPE:
        if parmas_a == CTROL_NEFBD:
            send = CTROL_PREDIX + bytearray(9)
            send[TYPE_LOCATION] = int(parmas_a)
            send[TYPE_LOCATION + 1] = int(parmas_b)
            dev = b'dev0' + str(pa).encode('ascii')
            send[TYPE_LOCATION + 2:TYPE_LOCATION + 8] = ccn_experiment.DEVICE_DICT[dev]
        elif parmas_a == CTROL_CHANG:
            send = CTROL_PREDIX + bytearray(10)
            send[TYPE_LOCATION] = int(parmas_a)
            send[TYPE_LOCATION + 1] = 1
            send[TYPE_LOCATION + 2:TYPE_LOCATION + 5] = pa[0:5]
        elif parmas_a == CTROL_LEDON:
            send = CTROL_PREDIX + bytearray(3)
            send[TYPE_LOCATION] = int(parmas_a)
            send[TYPE_LOCATION + 1] = pa[0]
        elif parmas_a == CTROL_TIMEX:
            send = CTROL_PREDIX + bytearray(2)
            send[TYPE_LOCATION] = int(parmas_a)
        else:
            return
    elif req_type == TEMPR_TYPE:
        send = TEMPR_PREFIX
    elif req_type == REMOT_TYPE:
        taget_device = b'dev0' + str(parmas_a).encode('ascii')
        if parmas_b == '1':
            req_name = taget_device + CTROL
            send = bytearray(b'\x00\x00\x00' + req_name) + bytearray(12)
            send[23] = int(CTROL_NEFBD)
            send[24] = int(CTROL_NEFBD_ADD)
            forbit_dev = b'dev0' + str(pa).encode('ascii')
            send[25: 31] = ccn_experiment.DEVICE_DICT[forbit_dev]
        elif parmas_b == '2':
            req_name = taget_device + CTROL
            send = bytearray(b'\x00\x00\x00' + req_name) + bytearray(12)
            send[23] = int(CTROL_LEDON)
            send[24] = int(pa)
        elif parmas_b == '3':
            content_name = pa.encode('ascii')
            if len(content_name) <= 14:
                full_name = bytearray(14)
                full_name[0: len(content_name)] = content_name
                req_name = taget_device + b'/' + full_name
                send = bytearray(b'\x00\x00\x00' + req_name) + bytearray(14)
                send[35] = 88
                send[36] = 2
            else:
                print('Content name is too long')
                return
            pass
    else:
        return
    serialComm.pppsend(ser, send)


def readfxn(ser):
    global NAME
    global DEVICE_CRTOL
    global DEVICE_INFOM
    global DEVICE_TEMPR

    writeindex = b'\xff\xff\xff'
    readindex = b'\xfe\xfe\xfe'
    recvdata = b'\xfd\xfd\xfd'
    reqdate = b'\xfc\xfc\xfc'
    sendcursor = b'\xdd\xdd\xdd'
    interval = b'\xcc\xcc\xcc'

    while True:
        frame, recvlen = serialComm.pppread(ser, 1024)
        print()
        print(frame[0: recvlen])
        if frame[4:7] == writeindex:
            print('ready to write index {}'.format(frame[7]))
        elif frame[4:7] == readindex:
            print('ready to read index {}'.format(frame[7]))
        elif frame[4:7] == recvdata:
            print('recv a fragment {}'.format(frame[7] + (frame[8] << 8)))
        elif frame[4:7] == reqdate:
            print('req data fragment {}, len {}'.format(frame[7] + (frame[8] << 8), frame[9]))
        elif frame[4:7] == sendcursor:
            print('send cursor {}'.format(frame[7]))
        elif frame[4:7] == interval:
            print('send interval {}'.format(frame[7]))
        if frame[6] == 0xff:
            csname = frame[7:27]
            if csname == DEVICE_CRTOL:
                if frame[28] == 0x04:
                    print('返回---', '点亮', NAME.decode('utf-8'), 'LED的控制信息')
                    if frame[27] == 0x00:
                        print('状态---', '成功')
                    else:
                        print('状态---', '未知错误')
            elif csname == DEVICE_INFOM:

                # 邻居表
                if frame[28] == 0x00:
                    print('返回---', '请求', NAME.decode('utf-8'), '的邻居列表')
                    period = 15
                    if frame[27] == 0x00:
                        print('状态---', '正常')
                        for count in range(0, frame[29]):
                            print('Neighbour No.{}  \t'.format(count + 1), end='')
                            name = getstr(frame[30 + count * period:36 + count * period])
                            print('name: {}  \t'.format(name), end='')
                            print('macadr: ', end='')
                            for mac in frame[36 + count * period:42 + count * period]:
                                print(' {:0>2x}'.format(mac), end='')
                            print('\tvalid_flag: {}'.format(frame[42 + count * period]), end='')
                            print('\tforbid_flag: {}'.format(frame[43 + count * period]), end='')
                            print('\trelation: {}'.format(frame[44 + count * period]), end='')
                            print()
                    elif frame[27] == 0x01:
                        print('状态---', '邻居数量异常（堆污染）')
                    else:
                        print('状态---', '未知状态')

                # 内容表
                elif frame[28] == 0x01:
                    print('返回---', '请求', NAME.decode('utf-8'), '的内容列表')
                    if frame[27] == 0x00:
                        print('状态---', '正常')
                        period = 40
                        for count in range(0, frame[29]):
                            print('CS No.{} \t'.format(count + 1), end='')
                            name = getstr(frame[30 + count * period:50 + count * period])
                            print('name: {:<20} \t'.format(name), end='')
                            # print('isRemote: {} \t'.format(frame[50 + count * period]), end='')
                            print('isCache: {} \t'.format(frame[51 + count * period]), end='')
                            print('isBroadCast: {} \t'.format(frame[52 + count * period]), end='')
                            print('hasCached: {} \t'.format(frame[53 + count * period]), end='')
                            pop = frame[54 + count * period] + (frame[55 + count * period] << 8)
                            print('popularity: {} \t'.format(pop), end='')
                            fresh_need = frame[56 + count * period] + (frame[57 + count * period] << 8)
                            print('freshNeed: {} \t'.format(fresh_need), end='')
                            rank = frame[58 + count * period] + (frame[59 + count * period] << 8)
                            print('rank: {} \t'.format(rank), end='')
                            # seqnum = frame[60 + count * period] + (frame[61 + count * period] << 8)
                            # print('seqnum: {} \t'.format(seqnum), end='')
                            last_req_time = frame[62 + count * period] + (frame[63 + count * period] << 8) + (
                                frame[64 + count * period] << 16) + (frame[65 + count * period] << 24)
                            print('lastReqTime: {} \t'.format(last_req_time), end='')
                            length = frame[66 + count * period] + (frame[67 + count * period] << 8) + (
                                frame[68 + count * period] << 16) + (frame[69 + count * period] << 24)
                            print('length: {} \t'.format(length))
                    elif frame[27] == 0x01:
                        print('状态---', '内容数量超过35')
                    else:
                        print('状态---', '未知状态')
                elif frame[28] == 0x02:
                    print('返回---', '请求', NAME.decode('utf-8'), '的转发信息库列表')
                    if frame[27] == 0x00:
                        print('状态---', '正常')
                        period = 31
                        for i in range(0, frame[29]):
                            print('FIB No.{}  \t'.format(i + 1), end='')
                            name = getstr(frame[30 + i * period:50 + i * period])
                            print('name: {}  \t'.format(name), end='')
                            length = frame[50 + i * period] + (frame[51 + i * period] << 8) + (
                                frame[52 + i * period] << 16) + (frame[53 + i * period] << 24)
                            print('length: {} \t'.format(length), end='')
                            print('hops: {}  \t'.format(frame[54 + i * period]), end='')
                            print('fowardmac: ', end='')
                            for abyte in frame[55 + i * period:61 + i * period]:
                                print(' {:0>2x}'.format(abyte), end='')
                            print()
                elif frame[28] == 0x04:
                    print('返回---', '请求', NAME.decode('utf-8'), '的PIT列表')
                    if frame[27] == 0x00:
                        print('状态---', '正常')
                        period = 36
                        for i in range(0, frame[29]):
                            print('PIT No.{}  \t'.format(i + 1), end='')
                            name = getstr(frame[30 + i * period:50 + i * period])
                            print('name: {}  \t'.format(name), end='')
                            seqnum = frame[50 + i * period] + (frame[51 + i * period] << 8)
                            print('seqnum: {} \t'.format(seqnum), end='')
                            pid = frame[52 + i * period] + (frame[53 + i * period] << 8)
                            print('ID: {}  \t'.format(pid), end='')
                            print('lastmac: ', end='')
                            for abyte in frame[54 + i * period:60 + i * period]:
                                print(' {:0>2x}'.format(abyte), end='')
                            print('  \tnextmac: ', end='')
                            for abyte in frame[60 + i * period:66 + i * period]:
                                print(' {:0>2x}'.format(abyte), end='')
                            print()
                    elif frame[27] == 0x01:
                        print('状态---', 'PIT条目数量超过20')
                    else:
                        print('状态---', '未知状态')
                elif frame[28] == 0x05:
                    print('返回---', '请求', NAME.decode('utf-8'), '的本地时间')
                    if frame[30] == 0x00:
                        print('时间状态：本地')
                    else:
                        print('时间状态：统一')
                    usec = frame[31] + (frame[32] << 8) + (frame[33] << 16) + (frame[34] << 24)
                    print('时间：', usec / 100, 'S ')

                # 缓存表
                elif frame[28] == 0x06:
                    print('返回---', '请求', NAME.decode('utf-8'), '的缓存信息')
                    period = 48
                    if frame[27] == 0x00:
                        print('状态---', '正常')
                        for i in range(0, frame[29]):
                            print('CACHE No.{} \t'.format(i + 1), end='')
                            name = getstr(frame[30 + i * period:50 + i * period])
                            print('name: {:<20} \t'.format(name), end='')
                            timestamp = frame[50 + i * period] + (frame[51 + i * period] << 8) + (
                                frame[52 + i * period] << 16) + (frame[53 + i * period] << 24)
                            print('born_time: {} \t'.format(timestamp), end='')
                            last_req_time = frame[54 + i * period] + (frame[55 + i * period] << 8) + (
                                frame[56 + i * period] << 16) + (frame[57 + i * period] << 24)
                            print('last_req_time: {} \t'.format(last_req_time), end='')
                            pop = frame[58 + i * period] + (frame[59 + i * period] << 8)
                            print('popularity: {} \t'.format(pop), end='')
                            fresh_need = frame[60 + i * period] + (frame[61 + i * period] << 8)
                            print('freshNeed: {} \t'.format(fresh_need), end='')
                            rank = frame[62 + i * period] + (frame[63 + i * period] << 8)
                            print('rank: {} \t'.format(rank), end='')
                            position = frame[64 + i * period]
                            print('postion: {} \t'.format(position), end='')
                            print('portList: ', end='')
                            for abyte in frame[66 + i * period:76 + i * period]:
                                print(' {:0>2x}'.format(abyte), end='')
                            print()
                else:
                    print('未知 infom 返回类型')
            elif csname == DEVICE_TEMPR:
                print('返回---', '请求', NAME.decode('utf-8'), '的温度信息 : ' + getstr(frame[32: 42]))
            else:
                pass
        # elif frame[6] == 0x01:
        #     target = b'test.mp4\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        #     if frame[7:27] == target:
        #         # fragment = frame[30] + (frame[31] << 8)
        #         for i in range(0, 256):
        #             sendbyte[i] = frame[30]
        #         send = frame[4:recvlen-1] + sendbyte
        #         send[2] = 0xff
        #         send[23] = 0xff
        #         # print(send)
        #         serialComm.pppsend(ser, send)


if __name__ == '__main__':
    connection_init()
    se = serial.Serial()
    try:
        print('Connection to ' + COM + '......')
        se = serial.Serial(COM, 115200)
        print('Connection Success\n')
    except serial.serialutil.SerialException as ex:
        print(ex)
    connect_try(se)
    t1 = threading.Thread(target=choose_fxn, args=(se, ), name='writeThread')
    t2 = threading.Thread(target=readfxn, args=(se, ), name='readThread')
    t1.start()
    t2.start()

# frame, frameLen = pppread(se, 1024)
# print('frame content: {}'.format(frame[0:frameLen]))
# log.info('recv a valid frame {}'.format(frameLen))
# log.info('frame content: {}'.format(frame[0:frameLen]))
