from PyQt6.QtWidgets import QWidget, QGridLayout

from ..common.constants import ButtonLavels as lvl
from ..util.motor_controller import MotorController
from ..common.button import Button


class MotorControlWidget(QWidget):
    """モーターコントロールウィジェット"""
    def __init__(self):
        """コンストラクタ

        Arguments:
            motor_controller -- MotorControllerオブジェクト
        """
        super().__init__()
        self.motor_controller = None
        self.init_ui()

    def init_ui(self):
        """UIの初期化"""
        layout = QGridLayout(self)

        self.motor_start_1 = Button(lvl.ELONG_X_LAVEL)
        self.motor_stop_1 = Button(lvl.SHRINK_X_LAVEL)
        self.motor_reverse_1 = Button(lvl.REVERS_X_LAVEL)
        self.motor_start_2 = Button(lvl.ELONG_Y_LAVEL)
        self.motor_stop_2 = Button(lvl.SHRINK_Y_LAVEL)
        self.motor_reverse_2 = Button(lvl.REVERS_Y_LAVEL)

        buttons = [
            (self.motor_start_1, 0, 0),
            (self.motor_stop_1, 0, 1),
            (self.motor_reverse_1, 0, 2),
            (self.motor_start_2, 1, 0),
            (self.motor_stop_2, 1, 1),
            (self.motor_reverse_2, 1, 2)
        ]

        for btn, row, col in buttons:
            layout.addWidget(btn, row, col)

    def init_signals(self):
        """シグナルを初期化する"""
        self.motor_controller.on_motor_x_reversed.connect(
            self.on_motor_x_reversed)
        self.motor_controller.on_motor_y_reversed.connect(
            self.on_motor_y_reversed)

    def on_motor_x_reversed(self):
        """motor_x_reversedに対するスロットメソッド"""
        self.toggle_button_text(self.motor_start_1,
                                lvl.ELONG_X_LAVEL, lvl.SHRINK_X_LAVEL)

    def on_motor_y_reversed(self):
        """motor_y_reversedに対するスロットメソッド"""
        self.toggle_button_text(self.motor_start_2,
                                lvl.ELONG_Y_LAVEL, lvl.SHRINK_Y_LAVEL)

    def toggle_button_text(self, button, text1, text2):
        """ボタンのテキストを切り替える"""
        button.setText(text2 if button.text() == text1 else text1)

    def set_motor_controller(self, motor_controller: MotorController):
        """MotorControllerオブジェクトをセットする

        Arguments:
            motor_controller -- MotorControllerオブジェクト
        """
        if self.motor_controller is not None:
            self.throw_motor_ctrl_error()
            return

        self.motor_controller = motor_controller
        self.init_signals()

    def throw_motor_ctrl_error(self):
        """MotorControllerが既にセットされているときエラー"""
        raise ValueError("MotorController has already been set")
