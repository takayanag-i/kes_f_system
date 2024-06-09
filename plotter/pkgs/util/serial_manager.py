import serial


class SerialManager:
    """シリアルマネージャ.
    """
    def __init__(self, baudrate=115200):
        """コンストラクタ.

        Keyword Arguments:
            baudrate -- ボーレート (default: {115200})
        """
        self.ser = None
        self.baudrate = baudrate
        self.is_ready = False

    def open_port(self, port):
        """シリアルをオープン.

        Arguments:
            port -- COMポート名
        """
        try:
            self.ser = serial.Serial(port, self.baudrate, timeout=None)
            print(f"Connected to {port}")
            if self.ser and self.ser.is_open:
                self.is_ready = True
        except Exception as e:
            print(f"Failed to connect to {port}: {e}")

    def close_port(self):
        """シリアルをクローズ.
        """
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Serial port closed")

    def write(self, data):
        """シリアルに書き込む.

        Arguments:
            data -- 値
        """
        if self.ser and self.ser.is_open:
            self.ser.write(data)

    def read_serial_data(self):
        """シリアルから値を読む.

        Returns: 一行分
        """
        try:
            input_serial = self.ser.readline().rstrip()
            return input_serial.decode()
        except (UnicodeDecodeError, ValueError):
            return None