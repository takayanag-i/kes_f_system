import logging

from PyQt6.QtWidgets import QComboBox
from PyQt6.QtCore import QTimer

from pkgs.common.constants import Styles, Commands, ArithmeticConstants
from pkgs.util.serial_manager import SerialManager, SerialManagerError
from pkgs.util.motor_controller import MotorController
from pkgs.util.plot_array_handler import (PlotArrayHandler,
                                          PlotArrayHandlerError)
from pkgs.gui.main_window import Window


# ロガーを設定
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Executor:
    def __init__(self):
        self.sm1 = SerialManager()
        self.sm2 = SerialManager()
        self.mc = MotorController(self.sm1)
        self.handler = PlotArrayHandler()
        self.window = Window()
        self.setup_event_handlers()

    def init_signal(self, sender: QComboBox, sm: SerialManager):
        def select_port_slot(index):
            port_name = sender.itemText(index)
            sm.close_port()
            sm.open_port(port_name)
            if sm.is_ready:
                self.show_message(f'{port_name}に接続しました', logging.INFO)
            self.enable_plot_start()

        signal = sender.currentIndexChanged
        signal.connect(select_port_slot)

    def enable_plot_start(self):
        if self.sm1.is_ready and self.sm2.is_ready:
            self.window.plot_start_button.setEnabled(True)

    def setup_event_handlers(self):

        # MainUI
        self.window.save_button.set_callback(self.save)
        self.window.plot_start_button.set_callback(self.plot_start)
        self.window.plot_stop_button.set_callback(self.plot_stop)
        self.window.plot_reset_button.set_callback(self.reset)
        self.window.exit_button.set_callback(self.exit)

        # MotorControllerUI
        self.window.motor_ui.start1.set_callback(
            self.mc.start_motor1)
        self.window.motor_ui.stop1.set_callback(
            self.mc.stop_motor1)
        self.window.motor_ui.reverse1.set_callback(
            self.mc.reverse_motor1)
        self.window.motor_ui.start2.set_callback(
            self.mc.start_motor2)
        self.window.motor_ui.stop2.set_callback(
            self.mc.stop_motor2)
        self.window.motor_ui.reverse2.set_callback(
            self.mc.reverse_motor2)

        # ComboBoxes
        self.init_signal(self.window.combobox1, self.sm1)
        self.init_signal(self.window.combobox2, self.sm2)

    def save(self):
        try:
            file_name = self.window.line_edit.text()
            self.handler.save_to_csv(file_name)
            self.show_message(f"{file_name}を保存しました", logging.INFO)
        except PlotArrayHandlerError as e:
            self.show_message(str(e), logging.ERROR)

    def plot_start(self):
        try:
            self.sm1.write(Commands.PLOT_START)
            self.window.plot_start_button.setStyleSheet("")
            self.window.plot_stop_button.setStyleSheet(Styles.STYLE_REJECT)
        except SerialManagerError as e:
            self.show_message(str(e), logging.ERROR)
            return

        self.window.plot_stop_button.setEnabled(True)
        self.timer = QTimer(self.window)  # QTimerのインスタンスをここで初期化
        self.timer.timeout.connect(self.update)
        self.num = 0
        self.timer.start(0)

    def plot_stop(self):
        try:
            self.sm1.write(Commands.PLOT_STOP)
        except SerialManagerError as e:
            self.show_message(str(e), logging.ERROR)
        finally:
            self.timer.stop()
            self.window.plot_stop_button.setEnabled(False)
            self.window.plot_stop_button.setStyleSheet("")
            self.window.plot_start_button.setEnabled(False)
            self.window.plot_start_button.setStyleSheet("")

        self.window.plot_reset_button.setEnabled(True)
        self.window.plot_reset_button.setStyleSheet(Styles.STYLE)

    def reset(self):
        self.handler.reset_data()
        self.window.plot_stop_button.setEnabled(False)
        self.window.plot_start_button.setEnabled(True)
        self.window.plot_start_button.setStyleSheet(Styles.STYLE)
        self.window.plot_reset_button.setEnabled(False)
        self.window.plot_reset_button.setStyleSheet("")

    def update(self):
        # 1行読み飛ばし
        if self.num == 0:
            try:
                self.sm1.read_serial_data()
                self.sm2.read_serial_data()
                self.num += 1
                return
            except SerialManagerError as e:
                self.show_message(str(e), logging.ERROR)
                return

        # 2回目以降の処理
        try:
            input1 = self.sm1.read_serial_data()
            input2 = self.sm2.read_serial_data()
        except SerialManagerError as e:
            self.show_message(str(e), logging.ERROR)
            return

        try:
            processed_data = self.handler.process_data(input1, input2)
            if processed_data is None:
                raise ValueError("データの処理に失敗しました")
        except ValueError as e:
            self.show_message(str(e), logging.ERROR)
            return

        # 2回目で初期時刻を格納
        if self.num == 1:
            self.t0 = processed_data[0]

        # 2回目以降の処理のつづき
        processed_data[0] -= self.t0
        self.handler.update_arrays(processed_data)

        if self.num % 5 == 0:
            plot_array = self.handler.update_plts(processed_data)
            t_plt = plot_array[0]
            y_plts = plot_array[1:]
            for curve, y_plt in zip(self.window.plot_area.curves, y_plts):
                curve.setData(t_plt, y_plt)

        self.num += 1

        if self.num >= ArithmeticConstants.DATA_LENGTH:
            self.timer.stop()
            self.show_message("データ長がオーバーしています", logging.WARNING)

    def exit(self):
        try:
            self.sm1.close_port()
            self.sm2.close_port()
            self.show_message('正常に終了しました', logging.INFO)
        except SerialManagerError as e:
            self.show_message(str(e), logging.ERROR)
        finally:
            self.window.close()

    def show_message(self, message, level):
        """メッセージを表示し、ログに記録する"""
        self.window.message_box.setText(message)
        if level == logging.INFO:
            logger.info(message)
        elif level == logging.WARNING:
            logger.warning(message)
        elif level == logging.ERROR:
            logger.error(message)
