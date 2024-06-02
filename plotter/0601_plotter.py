import sys
import datetime as dt

from PyQt6.QtWidgets import (QMainWindow, QWidget, QLineEdit, QGridLayout,
                             QApplication, QLabel, QComboBox)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QTimer
import numpy as np
import pandas as pd
import serial.tools.list_ports

from pkgs.common.button import Button
from pkgs.common.constants import (Styles,
                                   Formats as fmt,
                                   Commands as cmd,
                                   FontConfig as fnt,
                                   ArithmeticConstants as const)
from pkgs.util.serial_manager import SerialManager
from pkgs.util.motor_controller import MotorController
from pkgs.gui.multi_axis_graph import MultiAxisGraphWidget
from pkgs.gui.motor_ctrl_widget import MotorControlWidget
from pkgs.util.plot_array_handler import PlotArrayHandler


class Window(QMainWindow):
    """メインウィンドウクラス

    @Override QMainWindow
    """
    def __init__(self, executor):
        super().__init__()

        self.executor = executor
        self.executor.set_window(self)
        self.init_ui()

    def init_ui(self):
        """UIの初期化
        """
        self.setWindowTitle("KES-F System")
        self.setGeometry(100, 100, 800, 450)
        self.widget = QWidget()
        self.setCentralWidget(self.widget)
        self.layout = QGridLayout()
        self.widget.setLayout(self.layout)
        self.create_widgets()
        self.arrange_widgets()
        self.layout_widgets()

    def create_widgets(self):
        """ウィジェットの生成
        """
        self.plot_widget = MultiAxisGraphWidget()

        self.widget_for_comport = QWidget()
        self.widget_for_controller = MotorControlWidget(
            self.executor.motor_controller)

        # ボタン
        self.save_button = Button('Save', self.executor.save_func)
        self.plot_start_button = Button('Start',
                                        self.executor.plot_start_func, False)
        self.plot_stop_button = Button('Stop',
                                       self.executor.plot_stop_func, False)
        self.plot_reset_button = Button('Reset', self.executor.reset, False)
        self.exit_button = Button('Exit', self.executor.exit_func)

        # テキストエリア
        self.line_edit = QLineEdit(dt.datetime.now().strftime(fmt.DATE_FMT))
        self.message_box = QLabel('シリアルポートを選択してください')

        # コンボボックス
        self.combobox1 = QComboBox()
        self.combobox2 = QComboBox()

    def arrange_widgets(self):
        """ウィジェットの操作
        """
        self.plot_widget.setMinimumSize(800, 450)
        self.widget_for_comport.setMaximumHeight(160)
        self.line_edit.setFont(QFont(fnt.FONT_FAMILY, fnt.FONT_SIZE))

        # コンボボックス
        self.combobox1.addItems(self.executor.get_serial_ports())
        self.combobox1.currentIndexChanged.connect(
            self.executor.on_combobox1_changed)
        self.combobox1_label = QLabel('COM Port : ESP32 Dev Module')

        self.combobox2.addItems(self.executor.get_serial_ports())
        self.combobox2.currentIndexChanged.connect(
            self.executor.on_combobox2_changed)
        self.combobox2_label = QLabel('COM Port : RP2040 Xiao')

    def layout_widgets(self):
        """部品をレイアウトに追加
        """
        self.layout2 = QGridLayout()
        self.widget_for_comport.setLayout(self.layout2)
        # ウィジェット
        self.layout.addWidget(self.plot_widget, 0, 1)
        self.layout.addWidget(self.widget_for_comport, 0, 0)
        # ボタン
        self.layout.addWidget(self.save_button, 2, 0)
        self.layout.addWidget(self.plot_start_button, 3, 0)
        self.layout.addWidget(self.plot_stop_button, 4, 0)
        self.layout.addWidget(self.plot_reset_button, 5, 0)
        self.layout.addWidget(self.exit_button, 6, 0)
        # コンボボックス
        self.layout2.addWidget(self.combobox1_label, 0, 0)
        self.layout2.addWidget(self.combobox1, 1, 0)
        self.layout2.addWidget(self.combobox2_label, 2, 0)
        self.layout2.addWidget(self.combobox2, 3, 0)
        # テキストエリア
        self.layout.addWidget(self.line_edit, 2, 1)
        self.layout.addWidget(self.message_box, 6, 1)
        # コントローラ
        self.layout.addWidget(self.widget_for_controller, 3, 1, 4, 1)


class Executor:
    def __init__(self):
        self.sm1 = SerialManager()
        self.sm2 = SerialManager()
        self.motor_controller = MotorController(self.sm1)
        self.handler = PlotArrayHandler()

    def set_window(self, window):
        self.window = window

    def get_serial_ports(self):
        """接続可能なポート名を取得する

        Returns:
            ポート名のリスト
        """
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

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
        else:
            self.window.message_box\
                .setText(f"Failed to connect to {port_name}")

    def on_combobox2_changed(self, index):
        """上に同じ"""
        port_name = self.window.combobox2.itemText(index)
        self.sm2.close_port()
        self.sm2.open_port(port_name)
        if self.sm2.ser and self.sm2.ser.is_open:
            self.window.message_box\
                .setText(f"Connected to {port_name}")
        else:
            self.window.message_box\
                .setText(f"Failed to connect to {port_name}")

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

    def plot_start_func(self):
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

    def plot_stop_func(self):
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

    def exit_func(self):
        self.sm1.close_port()
        self.sm2.close_port()
        self.window.close()


def main():
    """メイン関数"""
    app = QApplication(sys.argv)
    executor = Executor()
    window = Window(executor)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
