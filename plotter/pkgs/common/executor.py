import logging

from PyQt6.QtWidgets import QComboBox
from PyQt6.QtCore import QTimer

from pkgs.common.constants import (Styles, Commands as cmd,
                                   ArithmeticConstants as const)
from pkgs.util.serial_manager import SerialManager, SerialManagerError
from pkgs.util.motor_controller import MotorController
from pkgs.util.plot_array_handler import PlotArrayHandler
from pkgs.gui.main_window import Window


# ロガーを設定
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Executor:
    def __init__(self):
        self.sm1 = SerialManager()
        self.sm2 = SerialManager()
        self.motor_controller = MotorController(self.sm1)
        self.handler = PlotArrayHandler()
        self.window = Window()
        self.setup_event_handlers()

    def connect_signal_and_slot(self, sender: QComboBox, sm: SerialManager):
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
        self.window.save_button.set_callback(self.handler.save_to_csv)
        self.window.plot_start_button.set_callback(self.plot_start)
        self.window.plot_stop_button.set_callback(self.plot_stop)
        self.window.plot_reset_button.set_callback(self.reset)
        self.window.exit_button.set_callback(self.exit)

        # MotorControllerUI
        self.window.motor_ui.motor_start_1.set_callback(
            self.motor_controller.start_motor_x)
        self.window.motor_ui.motor_stop_1.set_callback(
            self.motor_controller.stop_motor_x)
        self.window.motor_ui.motor_reverse_1.set_callback(
            self.motor_controller.reverse_motor_x)
        self.window.motor_ui.motor_start_2.set_callback(
            self.motor_controller.start_motor_y)
        self.window.motor_ui.motor_stop_2.set_callback(
            self.motor_controller.stop_motor_y)
        self.window.motor_ui.motor_reverse_2.set_callback(
            self.motor_controller.reverse_motor_y)

        # ComboBoxes
        self.connect_signal_and_slot(self.window.combobox1, self.sm1)
        self.connect_signal_and_slot(self.window.combobox2, self.sm2)

    def plot_start(self):
        try:
            self.sm1.write(cmd.PLOT_START)
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
            self.sm1.write(cmd.PLOT_STOP)
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
        except ValueError as e:
            self.show_message(str(e), logging.ERROR)
            return

        tmp1, tmp2, tmp3, tmp4, tmp5, tmp6 = processed_data

        # 2回目で初期時刻を格納
        if self.num == 1:
            self.t0 = tmp6

        # 2回目以降の処理のつづき
        tmp6 -= self.t0
        self.handler.update_arrays(tmp1, tmp2, tmp3, tmp4,
                                   tmp5, tmp6)

        if self.num % 5 == 0:
            t_plt, y1_plt, y2_plt, y3_plt, y4_plt, y5_plt\
                    = self.handler.update_plts(tmp1, tmp2, tmp3,
                                               tmp4, tmp5, tmp6)
            self.window.plot_widget.curve1.setData(t_plt, y1_plt)
            self.window.plot_widget.curve2.setData(t_plt, y2_plt)
            self.window.plot_widget.curve3.setData(t_plt, y3_plt)
            self.window.plot_widget.curve4.setData(t_plt, y4_plt)
            self.window.plot_widget.curve5.setData(t_plt, y5_plt)

        self.num += 1

        if self.num >= const.DATA_LENGTH:
            self.timer.stop()
            self.show_message("データ長がオーバーしています", logging.WARNING)

    def exit(self):
        try:
            self.sm1.close_port()
            self.sm2.close_port()
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
