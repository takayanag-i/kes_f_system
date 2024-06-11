from PyQt6.QtWidgets import QWidget, QGridLayout

from pkgs.common.constants import ButtonLabels
from pkgs.util.motor_controller import MotorController
from pkgs.gui.button import Button


class MotorControlWidget(QWidget):
    """モーターコントロールウィジェット"""
    def __init__(self):
        super().__init__()
        self.mc: MotorController = None
        self.init_ui()

    def init_ui(self):
        """UIの初期化"""
        layout = QGridLayout(self)

        self.start1 = Button(ButtonLabels.ELONG1)
        self.stop1 = Button(ButtonLabels.SHRINK1)
        self.reverse1 = Button(ButtonLabels.REVERSE1)
        self.start2 = Button(ButtonLabels.ELONG2)
        self.stop2 = Button(ButtonLabels.SHRINK2)
        self.reverse2 = Button(ButtonLabels.REVERSE2)

        buttons = [
            (self.start1, 0, 0),
            (self.stop1, 0, 1),
            (self.reverse1, 0, 2),
            (self.start2, 1, 0),
            (self.stop2, 1, 1),
            (self.reverse2, 1, 2)
        ]

        for btn, row, col in buttons:
            layout.addWidget(btn, row, col)

    def init_signals(self):
        """シグナルを初期化する"""
        self.mc.motor1_reversed_signal.connect(
            self.on_motor1_reversed)
        self.mc.motor2_reversed_signal.connect(
            self.on_motor2_reversed)

    def on_motor1_reversed(self):
        """motor1_reversed_signalに対するスロットメソッド"""
        self.toggle_button_text(
            self.start1, ButtonLabels.ELONG1, ButtonLabels.SHRINK1)

    def on_motor2_reversed(self):
        """motor2_reversed_signalに対するスロットメソッド"""
        self.toggle_button_text(
            self.start2, ButtonLabels.ELONG2, ButtonLabels.SHRINK2)

    def toggle_button_text(self, button: Button, text1, text2):
        """ボタンのテキストを切り替える"""
        button.setText(text2 if button.text() == text1 else text1)

    def set_motor_controller(self, mc: MotorController):
        """MotorControllerオブジェクトをセットする

        Arguments:
            motor_controller -- MotorControllerオブジェクト
        """
        if self.mc is not None:
            raise ValueError("MotorController has already been set")

        self.mc = mc
        self.init_signals()
