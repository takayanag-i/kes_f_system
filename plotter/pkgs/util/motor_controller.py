from PyQt6.QtCore import QObject, pyqtSignal
from .serial_manager import SerialManager

from pkgs.common.constants import Commands as cmd


class MotorController(QObject):
    """モーターコントローラ"""
    motor1_reversed_signal = pyqtSignal()
    motor2_reversed_signal = pyqtSignal()

    def __init__(self, serial_manager: SerialManager):
        """コンストラクタ

        Arguments:
            serial_manager -- SerialManagerオブジェクト
        """
        super().__init__()
        self.sm = serial_manager

    def start_motor1(self):
        """モーター1を開始する"""
        self.sm.write(cmd.MOTOR_START1)

    def stop_motor1(self):
        """モーター1を停止する"""
        self.sm.write(cmd.MOTOR_STOP1)

    def reverse_motor1(self):
        """モーター1を反転する"""
        self.sm.write(cmd.MOTOR_REVERSE1)
        self.motor1_reversed_signal.emit()

    def start_motor2(self):
        """モーター2を開始する"""
        self.sm.write(cmd.MOTOR_START2)

    def stop_motor2(self):
        """モーター2を停止する"""
        self.sm.write(cmd.MOTOR_STOP2)

    def reverse_motor2(self):
        """モーター2を反転する"""
        self.sm.write(cmd.MOTOR_REVERSE2)
        self.motor2_reversed_signal.emit()
