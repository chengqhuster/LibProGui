import serial
import logging
import datetime
import random

import serialComm

WAIT = 0
READY = 1
BUSY = 2
ESCAPING = 3
SUCCESS = 4
MAXFRAMELEN = 2000


def pppread(ser):
    logger = logging.getLogger(__name__)
    res = bytearray(MAXFRAMELEN)
    size = 0
    state = WAIT
    while state != SUCCESS:
        if size >= MAXFRAMELEN:
            size = 0
            state = WAIT
        try:
            recv = ser.read()
        except (serial.SerialException, IndexError):
            raise
        if state == WAIT:
            if recv[0] == 0x7e:
                res[size] = 0x7e
                size += 1
                state = READY
                logger.info('{0:<8} -> {1:<8}, append {2:>2x}, recvsize:{3:>4}'
                            .format('WAIT', 'READY', recv[0], size))
        elif state == READY:
            if recv[0] == 0xff:
                res[size] = 0xff
                size += 1
                state = BUSY
                logger.info('{0:<8} -> {1:<8}, append {2:>2x}, recvsize:{3:>4}'.
                            format('READY', 'BUSY', recv[0], size))
            elif recv[0] == 0x7e:
                pass
            else:
                size = 0
                state = WAIT
                logger.info('{0:<8} -> {1:<8}, invalid receive'.format('READY', 'WAIT'))
        elif state == BUSY:
            if recv[0] == 0x7d:
                state = ESCAPING
                logger.info('{0:<8} -> {1:<8}'.format('BUSY', 'ESCAPING'))
            elif recv[0] == 0x7e:
                res[size] = 0x7e
                size += 1
                bigend = res[3]
                smallend = res[2]
                validlen = bigend*256 + smallend
                if validlen == size:
                    state = SUCCESS
                    logger.info('{0:<8} -> {1:<8}, append {2:>2x}, recvsize:{3:>4}'
                                .format('BUSY', 'SUCCESS', recv[0], size))
                else:
                    size = 0
                    state = WAIT
                    logger.info('{0:<8} -> {1:<8}, {2} != {3}length check failed'
                                .format('BUSY', 'WAIT', size, validlen))
            else:
                res[size] = recv[0]
                size += 1
                logger.info('{0:<8} -> {1:<8}, append {2:>2x}, recvsize:{3:>4}'
                            .format('BUSY', 'BUSY', recv[0], size))
        elif state == ESCAPING:
            if recv[0] == 0x5e:
                res[size] = 0x7e
                size += 1
                state = BUSY
                logger.info('{0:<8} -> {1:<8}, append {2:>2x}, recvsize:{3:>4}'
                            .format('ESCAPING', 'BUSY', recv[0], size))
            elif recv[0] == 0x5d:
                res[size] = 0x7d
                size += 1
                state = BUSY
                logger.info('{0:<8} -> {1:<8}, append {2:>2x}, recvsize:{3:>4}'
                            .format('ESCAPING', 'BUSY', recv[0], size))
            else:
                size = 0
                state = WAIT
                logger.info('{0:<8} -> {1:<8}, invalid escaping'.format('ESCAPING', 'WAIT'))
        else:
            size = 0
            state = WAIT
            logger.info('{0:<8} -> {1:<8}, invalid state'.format('XXXXX', 'WAIT'))
    else:
        return res[0:size]


def getstr(frameblock):
    validnum = 0
    for letter in frameblock:
        if letter == 0x00:
            break
        else:
            validnum += 1
    if validnum == 0:
        return None
    else:
        try:
            strres = str(frameblock[0:validnum], encoding='ascii')
        except UnicodeDecodeError:
            strres = None
        return strres


def getmac(frameblock):
    if len(frameblock) != 6:
        return None
    else:
        macstr = '{:0>2X}:{:0>2X}:{:0>2X}:{:0>2X}:{:0>2X}:{:0>2X}'.\
            format(frameblock[0], frameblock[1], frameblock[2], frameblock[3], frameblock[4], frameblock[5])
        return macstr


# ser is serial.Serial type, mainframe is wx.Frame type
def recvfxn(ser, mainframe):
    # gtway = b'ReqForAConnection\x00\x00\x00'
    ctrol = b'/ctrol\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    infom = b'/infom\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    tempr = b'/tempr\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    while True:
        try:
            recmessage = pppread(ser)
            if recmessage[6] == 0xff:
                if recmessage[7:27] == mainframe.devicename + ctrol:
                    pass
                elif recmessage[7:27] == mainframe.devicename + infom:
                    if recmessage[28] == 0x00:
                        # 邻居列表
                        neighbor_table = mainframe.infoPanel.neighbor_table
                        row = neighbor_table.GetNumberRows()
                        if row != 0:
                            neighbor_table.DeleteRows(0, neighbor_table.GetNumberRows())
                        period = 13
                        # 返回状态正常
                        if recmessage[27] == 0x00:
                            for count in range(0, recmessage[29]):
                                neighbor_table.AppendRows(1)
                                name = getstr(recmessage[30 + count * period:36 + count * period])
                                if name is None:
                                    neighbor_table.SetCellValue(count, 0, 'Param Error')
                                    break
                                else:
                                    neighbor_table.SetCellValue(count, 0, name)
                                mac = getmac(recmessage[36 + count * period:42 + count * period])
                                if mac is None:
                                    neighbor_table.SetCellValue(count, 1, 'Param Error')
                                    break
                                else:
                                    neighbor_table.SetCellValue(count, 1, mac)
                        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        mainframe.infoPanel.neighbor_text.SetLabelText('Neighbor Table\nSnapshot : ' + time)
                        mainframe.infoPanel.GetSizer().Layout()
                        mainframe.infoPanel.Refresh()
                    elif recmessage[28] == 0x01:
                        # 内容列表
                        cs_table = mainframe.infoPanel.cs_table
                        row = cs_table.GetNumberRows()
                        if row != 0:
                            cs_table.DeleteRows(0, cs_table.GetNumberRows())
                        period = 28
                        # 返回状态正常
                        if recmessage[27] == 0x00:
                            for count in range(0, recmessage[29]):
                                cs_table.AppendRows(1)
                                name = getstr(recmessage[30 + count * period:50 + count * period])
                                if name is None:
                                    cs_table.SetCellValue(count, 0, 'Param Error')
                                    break
                                else:
                                    cs_table.SetCellValue(count, 0, name)
                                seqnum = recmessage[50 + count * period] + (recmessage[51 + count * period] << 8)
                                cs_table.SetCellValue(count, 1, '{:d}'.format(seqnum))
                                length = recmessage[52 + count * period] + (recmessage[53 + count * period] << 8) + (
                                    recmessage[54 + count * period] << 16) + (recmessage[55 + count * period] << 24)
                                cs_table.SetCellValue(count, 2, '{:d}'.format(length))
                        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        mainframe.infoPanel.cs_text.SetLabelText('Cs Table\nSnapshot : ' + time)
                        mainframe.infoPanel.GetSizer().Layout()
                        mainframe.infoPanel.Refresh()
                    elif recmessage[28] == 0x02:
                        # 信息转发表
                        fib_table = mainframe.infoPanel.fib_table
                        row = fib_table.GetNumberRows()
                        if row != 0:
                            fib_table.DeleteRows(0, fib_table.GetNumberRows())
                        period = 31
                        # 返回状态正常
                        if recmessage[27] == 0x00:
                            for count in range(0, recmessage[29]):
                                fib_table.AppendRows(1)
                                name = getstr(recmessage[30 + count * period:50 + count * period])
                                if name is None:
                                    fib_table.SetCellValue(count, 0, 'Param Error')
                                    break
                                else:
                                    fib_table.SetCellValue(count, 0, name)
                                length = recmessage[50 + count * period] + (recmessage[51 + count * period] << 8) + (
                                    recmessage[52 + count * period] << 16) + (recmessage[53 + count * period] << 24)
                                fib_table.SetCellValue(count, 1, '{:d}'.format(length))
                                hops = recmessage[54 + count * period]
                                fib_table.SetCellValue(count, 2, '{:d}'.format(hops))
                                mac = getmac(recmessage[55 + count * period:61 + count * period])
                                if mac is None:
                                    fib_table.SetCellValue(count, 3, 'Param Error')
                                    break
                                else:
                                    fib_table.SetCellValue(count, 3, mac)
                        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        mainframe.infoPanel.fib_text.SetLabelText('Fib Table\nSnapshot : ' + time)
                        mainframe.infoPanel.GetSizer().Layout()
                        mainframe.infoPanel.Refresh()
        except (serial.SerialException, IndexError):
            print('An exception happened')
            return


def connect_try(ser, welcomeframe):
    gtret = b'ReqForAConnection_OK'
    send = bytearray(b'\x00\x00\x01ReqForAConnection\x00\x00\x00')
    send[0] = random.randint(0, 255)
    send[1] = random.randint(0, 255)
    serialComm.pppsend(ser, send)
    while True:
        try:
            recmessage = pppread(ser)
            if recmessage[6] == 0xff and recmessage[7:27] == gtret:
                welcomeframe.connectFlag = True
                welcomeframe.deviceName = recmessage[27:32]
                welcomeframe.macAdr = recmessage[32:38]
                break
        except (serial.SerialException, IndexError) as e:
            print('line 234: An exception happened', e)
            return

# se = serial.Serial('COM4', 38400, parity=serial.PARITY_EVEN, rtscts=1)

# recvfxn(se)

# test = b'\x7e\x7e\x7e'
# res = getstr(test)
# print(res)
