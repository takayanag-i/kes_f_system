import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
import numpy as np
import pandas as pd

from pkgs.common.constants import (Styles, Commands as cmd,
                                   ArithmeticConstants as const)
from pkgs.util.serial_manager import SerialManager
from pkgs.util.motor_controller import MotorController
from pkgs.util.plot_array_handler import PlotArrayHandler
from pkgs.gui.main_window import Window


class Executor:
    def __init__(self):
        self.sm1 = SerialManager()
        self.sm2 = SerialManager()
        self.motor_controller = MotorController(self.sm1)
        self.handler = PlotArrayHandler()

        self.window = Window()

        self.window.combobox1\
            .currentIndexChanged.connect(self.on_combobox1_changed)
        self.window.combobox2\
            .currentIndexChanged.connect(self.on_combobox2_changed)

        self.set_buttons_listner()

    def on_combobox1_changed(self, index):
        """コンボボックスの値が変更されたときの処理.

        スロットメソッド
        選択されたポートをオープンしてラインテキストを変更

        Arguments:
            index -- インデックス
            呼び出し元のシグナルcurrentIndexChangedから受け取る
        """
        port_name = self.window.combobox1.itemText(index)
        self.sm1.close_port()
        self.sm1.open_port(port_name)
        if self.sm1.ser and self.sm1.ser.is_open:
            self.window.message_box\
                .setText(f"Connected to {port_name}")

    def on_combobox2_changed(self, index):
        """上に同じ"""
        port_name = self.window.combobox2.itemText(index)
        self.sm2.close_port()
        self.sm2.open_port(port_name)
        if self.sm2.ser and self.sm2.ser.is_open:
            self.window.message_box\
                .setText(f"Connected to {port_name}")

    def set_buttons_listner(self):
        self.window.save_button.set_callback(self.save_func)
        self.window.plot_start_button.set_callback(self.plot_start)
        self.window.plot_stop_button.set_callback(self.plot_stop)
        self.window.plot_reset_button.set_callback(self.reset)
        self.window.exit_button.set_callback(self.exit)

        self.window.widget_for_controller.motor_start_1.set_callback(
            self.motor_controller.start_motor_x)
        self.window.widget_for_controller.motor_stop_1.set_callback(
            self.motor_controller.stop_motor_x)
        self.window.widget_for_controller.motor_reverse_1.set_callback(
            self.motor_controller.reverse_motor_x)
        self.window.widget_for_controller.motor_start_2.set_callback(
            self.motor_controller.start_motor_y)
        self.window.widget_for_controller.motor_stop_2.set_callback(
            self.motor_controller.stop_motor_y)
        self.window.widget_for_controller.motor_reverse_2.set_callback(
            self.motor_controller.reverse_motor_y)

    def save_func(self):
        """データをCSVに保存する
        """
        array = np.append(np.array([self.handler.t,
                                    self.handler.y1,
                                    self.handler.y2,
                                    self.handler.y3,
                                    self.handler.y4,
                                    self.handler.y5]), axis=0)
        array = array.T
        columns = ['Time', 'F1', 'F2', 'Disp1', 'Disp2', 'Sensor']
        data = pd.DataFrame(array, columns=columns)
        data.to_csv(f"{self.window.line_edit.text()}.csv", index=False)

    def plot_start(self):
        self.handler.reset_data()
        self.window.plot_stop_button.setEnabled(True)
        try:
            self.sm1.write(cmd.PLOT_START)
            self.window.plot_start_button.setStyleSheet("")
            self.window.plot_start_button.setText('・・・')
            self.window.plot_stop_button.setStyleSheet(Styles.STYLE_REJECT)
        except Exception as e:
            self.window.plot_start_button.setText('エラー！')
            self.window.message_box.setText(f"Error: {e}")
        self.timer = QTimer(self.window)  # QTimerのインスタンスをここで初期化
        self.timer.timeout.connect(self.update)
        self.num = 0
        self.timer.start(0)

    def plot_stop(self):
        self.timer.stop()
        self.window.plot_stop_button.setEnabled(False)
        self.window.plot_stop_button.setStyleSheet("")
        self.sm1.write(cmd.PLOT_STOP)
        self.window.plot_reset_button.setEnabled(True)
        self.window.plot_reset_button.setStyleSheet(Styles.STYLE)

    def reset(self):
        self.handler.reset_data()
        self.window.plot_stop_button.setEnabled(False)
        self.window.plot_start_button.setEnabled(True)
        self.window.plot_start_button.setStyleSheet(Styles.STYLE)

    def update(self):
        input1 = self.sm1.read_serial_data()
        input2 = self.sm2.read_serial_data()

        if input1 and input2:
            processed_data = self.handler.process_data(input1, input2)
            if processed_data:
                tmp1, tmp2, tmp3, tmp4, tmp5, tmp6 = processed_data
                if self.num == 0:
                    self.t0 = tmp6
                tmp6 -= self.t0
                self.handler.update_arrays(tmp1, tmp2, tmp3,
                                           tmp4, tmp5, tmp6)
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

    def exit(self):
        self.sm1.close_port()
        self.sm2.close_port()
        self.window.close()


def main():
    """メイン関数"""
    app = QApplication(sys.argv)
    executor = Executor()
    executor.window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
