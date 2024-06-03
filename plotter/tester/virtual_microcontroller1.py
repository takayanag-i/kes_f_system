import serial
import time
import random


def virtual_microcontrollers():
    """仮想マイクロコントローラ
    """
    ser1 = serial.Serial('/dev/ttys014', 115200)  # [1]
    ser2 = serial.Serial('/dev/ttys013', 115200)  # [2]
    while True:
        disp1 = random.uniform(0, 100)
        disp2 = random.uniform(0, 100)
        tm = int(time.time() * 1000000)  # μ秒単位のタイムスタンプ
        data = f'{disp1},{disp2},{tm}\n'
        ser1.write(data.encode)
        time.sleep(1)


if __name__ == '__main__':
    virtual_microcontrollers()
