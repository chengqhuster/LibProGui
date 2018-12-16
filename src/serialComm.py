# import serial
# import serial.tools.list_ports as lport
import logging
import random

WAIT = 0
READY = 1
BUSY = 2
ESCAPING = 3
SUCCESS = 4


def pppread(ser, length):
    logger = logging.getLogger(__name__)
    res = bytearray(length)
    size = 0
    state = WAIT
    while state != SUCCESS:
        if size >= length:
            size = 0
            state = WAIT
        recv = ser.read()
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
                    logger.info('{0:<8} -> {1:<8}, {2} != {3}length check failed'.format('BUSY', 'WAIT', size, validlen))
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
        return res, size


def pppsend(ser, frame):
    res = bytearray(2048)
    count = 0
    size = 0
    res[count] = 0x7e
    count += 1
    res[count] = 0xff
    # 留出length字段
    count += 3
    frame[0] = random.randint(0, 255)
    frame[1] = random.randint(0, 255)
    for abyte in frame:
        size += 1
        if abyte == 0x7e:
            res[count] = 0x7d
            count += 1
            res[count] = 0x5e
            count += 1
        elif abyte == 0x7d:
            res[count] = 0x7d
            count += 1
            res[count] = 0x5d
            count += 1
        else:
            res[count] = abyte
            count += 1
    res[count] = 0x7e
    count += 1
    size += 5
    res[3] = size//256
    res[2] = size - res[3]*256
    ser.write(res[0: count])
