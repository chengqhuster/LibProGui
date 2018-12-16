import threading, time


def do_thread_test(a, b):
    print(a, b)
    print('Start time', time.strftime('%H:%M:%S'))
    time.sleep(1)
    print('Stop time', time.strftime('%H:%M:%S'))

if __name__ == '__main__':
    aa = 1
    bb = 2
    t = threading.Thread(target=do_thread_test, args=(aa, bb))
    t.setDaemon(True)
    t.start()
    t.join(5)
    print('Main Stop time', time.strftime('%H:%M:%S'))
