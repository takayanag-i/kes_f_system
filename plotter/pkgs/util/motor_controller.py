from PyQt6.QtCore import QObject, pyqtSignal
from .serial_manager import SerialManager

from pkgs.common.constants import Commands as cmd


class MotorController(QObject):
    """モーターコントローラ"""
    on_motor_x_reversed = pyqtSignal()
    on_motor_y_reversed = pyqtSignal()

    def __init__(self, serial_manager: SerialManager):
        """コンストラクタ

        Arguments:
            serial_manager -- SerialManagerオブジェクト
        """
        super().__init__()
        self.sm = serial_manager

    def start_motor_x(self):
        """X軸モーターを開始する"""
        self.sm.write(cmd.MOTOR_X_START)

    def stop_motor_x(self):
        """X軸モーターを停止する"""
        self.sm.write(cmd.MOTOR_X_STOP)

    def reverse_motor_x(self):
        """X軸モーターの回転を反転する"""
        self.sm.write(cmd.MOTOR_X_REVERSE)
        self.on_motor_x_reversed.emit()

    def start_motor_y(self):
        """Y軸モーターを開始する"""
        self.sm.write(cmd.MOTOR_Y_START)

    def stop_motor_y(self):
        """Y軸モーターを停止する"""
        self.sm.write(cmd.MOTOR_Y_STOP)

    def reverse_motor_y(self):
        """Y軸モーターの回転を反転する"""
        self.sm.write(cmd.MOTOR_Y_REVERSE)
        self.on_motor_y_reversed.emit()
