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
            if self.ser and self.ser.is_open:
                self.is_ready = True
        except serial.SerialException as e:
            self.is_ready = False
            self.ser = None
            raise RuntimeError(f"{port} に接続できませんでした: {e}")
        except Exception as e:
            self.is_ready = False
            self.ser = None
            raise RuntimeError(f"{port} に接続中に予期しないエラーが発生しました: {e}")

    def close_port(self):
        """シリアルをクローズ.
        """
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
            except Exception as e:
                raise RuntimeError(f"ポートを閉じる際に予期しないエラーが発生しました: {e}")

    def write(self, data):
        """シリアルに書き込む.

        Arguments:
            data -- 値
        """
        if self.ser and self.ser.is_open:
            try:
                self.ser.write(data)
            except serial.SerialTimeoutException as e:
                raise RuntimeError(f"書き込みタイムアウトが発生しました: {e}")
            except Exception as e:
                raise RuntimeError(f"データを書き込む際に予期しないエラーが発生しました: {e}")

    def read_serial_data(self):
        """シリアルから値を読む.

        Returns: 一行分
        """
        if self.ser and self.ser.is_open:
            try:
                input_serial = self.ser.readline().rstrip()
                return input_serial.decode()
            except UnicodeDecodeError as e:
                raise RuntimeError(f"Unicode デコードエラーが発生しました: {e}")
            except ValueError as e:
                raise RuntimeError(f"値エラーが発生しました: {e}")
            except Exception as e:
                raise RuntimeError(f"データを読み取る際に予期しないエラーが発生しました: {e}")
        else:
            raise RuntimeError("シリアルポートが開いていません")
