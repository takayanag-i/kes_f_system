from PyQt6.QtWidgets import QWidget, QGridLayout

from pkgs.common.constants import ButtonLavels as lv
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

        self.start1 = Button(lv.ELONG_LAVEL1)
        self.stop1 = Button(lv.SHRINK_LAVEL1)
        self.reverse1 = Button(lv.REVERS_LAVEL1)
        self.start2 = Button(lv.ELONG_LAVEL2)
        self.stop2 = Button(lv.SHRINK_LAVEL2)
        self.reverse2 = Button(lv.REVERS_LAVEL2)

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
        self.toggle_button_text(self.start1,
                                lv.ELONG_LAVEL1, lv.SHRINK_LAVEL1)

    def on_motor2_reversed(self):
        """motor2_reversed_signalに対するスロットメソッド"""
        self.toggle_button_text(self.start2,
                                lv.ELONG_LAVEL2, lv.SHRINK_LAVEL2)

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
