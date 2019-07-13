import schedule
import time
import threading
import random

MARK = 0
PRINT_LIST = {0: 'HELLO',
              1: 'EVERY',
              2: 'ONE'}


def job():
    global MARK
    global PRINT_LIST
    print("I'm working..." + PRINT_LIST[MARK])
    MARK = (MARK + 1) % 3
    time.sleep(4)
    print("Finish work")


def pak():
    t = time.time()
    print(t)
    print(int(t))
    print(round(t * 1000))
    t = threading.Thread(target=job, name='print thread')
    t.setDaemon(True)
    t.start()

if __name__ == '__main__':
    print(65535 % 256)
    print(65535//256)
    a = 'acdvd'
    print(a[1:4])
    tt = bytearray(b'\x00\x00\x00\x00\x00\x00')

    while True:
        length = tt.count(0)
        if length == 0:
            break
        choose = random.randint(1, length)
        for i in range(len(tt)):
            if tt[i] == 0:
                choose -= 1
            if choose == 0:
                # 请求第 i 个内容
                print('choose : {}'.format(i))
                tt[i] = 1
                break
    print(tt)

    schedule.every(4).seconds.do(pak)
    while True:
        schedule.run_pending()
        time.sleep(0.5)
