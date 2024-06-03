import serial
import time
import random


def virtual_microcontrollers():
    """仮想マイクロコントローラ
    """
    ser1 = serial.Serial('/dev/ttys037', 115200)  # [1]
    ser2 = serial.Serial('/dev/ttys036', 115200)  # [2]
    while True:
        disp1 = random.uniform(0, 10)
        disp2 = random.uniform(0, 10)
        tm = int(time.time() * 1000000)  # μ秒単位のタイムスタンプ
        d = random.uniform(0, 4095)
        f1 = random.uniform(0, 4095)
        f2 = random.uniform(0, 4095)
        data1 = f'{disp1},{disp2},{tm}\n'
        data2 = f'{d},{f1},{f2}\n'
        ser1.write(data1.encode())
        print("lorem")
        ser2.write(data2.encode())
        # time.sleep(1)


if __name__ == '__main__':
    virtual_microcontrollers()
