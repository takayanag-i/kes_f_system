import sys
import datetime

from PyQt6.QtWidgets import (QMainWindow, QPushButton, QWidget,
                             QGraphicsWidget, QLineEdit, QGridLayout,
                             QApplication, QLabel, QComboBox)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QTimer, QObject, pyqtSignal
import numpy as np
import serial
import pyqtgraph as pg
import pandas as pd
import serial.tools.list_ports


MICRO_TO_UNIT = 1000000
DATA_LENGTH = int(2**20)
BAUDRATE = 115200

# モータ制御コマンド
PLOT_START = b'0'
PLOT_STOP = b'1'

MOTOR_X_START = b'3'
MOTOR_X_STOP = b'4'
MOTOR_X_REVERSE = b'5'

MOTOR_Y_START = b'7'
MOTOR_Y_STOP = b'8'
MOTOR_Y_REVERSE = b'9'

# 軸ラベル
TIME_AX_LAVEL = 'Time / s</font>'
FORCE_AX_LAVEL = 'Force / N</font>'
DISP_AX_LAVEL = 'Displacement / mm</font>'
SENSOR_AX_LAVEL = 'Sensor Output / V</font>'

ELONG_X_LAVEL = 'Xのばす'
SHRINK_X_LAVEL = 'X縮める'
REVERS_X_LAVEL = 'X逆回転'
ELONG_Y_LAVEL = 'Yのばす'
SHRINK_Y_LAVEL = 'Y縮める'
REVERS_Y_LAVEL = 'Y逆回転'

# フォント
FONT_FAMILY = 'Arial'
FONT_SIZE = 12

# ボタンスタイル
STYLE = """
QPushButton {
    border: none;
    background-color: #3498db;
    color: #fff;
    padding: 10px 20px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #2980b9;
}
QPushButton:pressed {
    background-color: #1b4f72;
}
"""
STYLE_REJECT = """
QPushButton {
    border: none;
    background-color: #e74c3c;
    color: #fff;
    padding: 10px 20px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #c0392b;
}
QPushButton:pressed {
    background-color: #922b21;
}
"""


class SerialManager:
    """シリアルマネージャ.
    """
    def __init__(self, baudrate=BAUDRATE):
        """コンストラクタ.

        Keyword Arguments:
            baudrate -- ボーレート (default: {BAUDRATE})
        """
        self.ser = None
        self.baudrate = baudrate

    def open_port(self, port):
        """シリアルをオープン.

        Arguments:
            port -- COMポート名
        """
        try:
            self.ser = serial.Serial(port, self.baudrate, timeout=None)
            print(f"Connected to {port}")
        except Exception as e:
            print(f"Failed to connect to {port}: {e}")

    def close_port(self):
        """シリアルをクローズ.
        """
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Serial port closed")

    def write(self, data):
        """シリアルに書き込む.

        Arguments:
            data -- 値
        """
        if self.ser and self.ser.is_open:
            self.ser.write(data)

    def read_serial_data(self):
        """シリアルから値を読む.

        Returns: 一行分
        """
        try:
            input_serial = self.ser.readline().rstrip()
            return input_serial.decode()
        except (UnicodeDecodeError, ValueError):
            return None


class Window(QMainWindow):
    """メインウィンドウクラス

    Arguments:
        QMainWindow -- 親クラス
    """
    def __init__(self):
        super().__init__()
        self.sm1 = SerialManager()
        self.sm2 = SerialManager()
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

    def create_widgets(self):
        """ウィジェットの生成
        """
        self.plot_widget = MultiAxisGraphWidget()
        self.plot_widget.setMinimumSize(800, 450)
        self.plot_manager = PlotArrayHandler(self.plot_widget)

        self.widget_for_comport = QWidget()
        self.widget_for_comport.setMaximumHeight(160)
        self.layout2 = QGridLayout()
        self.widget_for_comport.setLayout(self.layout2)

        self.motor_controller = MotorController(self.sm1)  # 1つ目のシリアルポートを使う
        self.widget_for_controller = MotorControlWidget(self.motor_controller)

        self.save_button = create_btn('Save', self.save_func)
        self.plot_start_button = create_btn(
            'Start', self.plot_start_func, False
        )
        self.plot_stop_button = create_btn(
            'Stop', self.plot_stop_func, False
        )
        self.plot_reset_button = create_btn(
            'Reset', self.reset, False
        )
        self.exit_button = create_btn('Exit', self.exit_func)

        dt = datetime.datetime.now()
        line_text = dt.strftime('%Y-%m%d-%H%M-プロジェクト名')
        self.line_edit = QLineEdit(line_text)
        # self.line_edit.setFocus()
        self.line_edit.setFont(QFont(FONT_FAMILY, FONT_SIZE))

        self.message_box = QLabel('シリアルポートを選択してください')

        self.combobox1 = QComboBox()
        self.combobox1.addItems(self.get_serial_ports())
        self.combobox1.currentIndexChanged.connect(self.on_combobox1_changed)
        self.combobox1_label = QLabel('COM Port : ESP32 Dev Module')

        self.combobox2 = QComboBox()
        self.combobox2.addItems(self.get_serial_ports())
        self.combobox2.currentIndexChanged.connect(self.on_combobox2_changed)
        self.combobox2_label = QLabel('COM Port : RP2040 Xiao')

    def arrange_widgets(self):
        """部品をレイアウトに追加
        """
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
        port_name = self.combobox1.itemText(index)
        self.sm1.close_port()
        self.sm1.open_port(port_name)
        if self.sm1.ser and self.sm1.ser.is_open:
            self.message_box.setText(f"Connected to {port_name}")
        else:
            self.message_box.setText(f"Failed to connect to {port_name}")

    def on_combobox2_changed(self, index):
        """上に同じ"""
        port_name = self.combobox2.itemText(index)
        self.sm2.close_port()
        self.sm2.open_port(port_name)
        if self.sm2.ser and self.sm2.ser.is_open:
            self.message_box.setText(f"Connected to {port_name}")
        else:
            self.message_box.setText(f"Failed to connect to {port_name}")

    def save_func(self):
        """データをCSVに保存する
        """
        array = np.append(np.array([self.plot_manager.t,
                                    self.plot_manager.y1,
                                    self.plot_manager.y2,
                                    self.plot_manager.y3,
                                    self.plot_manager.y4,
                                    self.plot_manager.y5]), axis=0)
        array = array.T
        columns = ['Time', 'F1', 'F2', 'Disp1', 'Disp2', 'Sensor']
        data = pd.DataFrame(array, columns=columns)
        data.to_csv(f"{self.line_edit.text()}.csv", index=False)

    def plot_start_func(self):
        self.plot_manager.reset_data()
        self.plot_stop_button.setEnabled(True)
        try:
            self.sm1.write(PLOT_START)
            self.plot_start_button.setStyleSheet("")
            self.plot_start_button.setText('・・・')
            self.plot_stop_button.setStyleSheet(STYLE_REJECT)
        except Exception as e:
            self.plot_start_button.setText('エラー！')
            self.message_box.setText(f"Error: {e}")
        self.timer = QTimer(self)  # QTimerのインスタンスをここで初期化
        self.timer.timeout.connect(self.update)
        self.num = 0
        self.timer.start(0)

    def plot_stop_func(self):
        self.timer.stop()
        self.plot_stop_button.setEnabled(False)
        self.plot_stop_button.setStyleSheet("")
        self.sm1.write(PLOT_STOP)
        self.plot_reset_button.setEnabled(True)
        self.plot_reset_button.setStyleSheet(STYLE)

    def reset(self):
        self.plot_manager.reset_data()
        self.plot_stop_button.setEnabled(False)
        self.plot_start_button.setEnabled(True)
        self.plot_start_button.setStyleSheet(STYLE)

    def update(self):
        input1 = self.sm1.read_serial_data()
        input2 = self.sm2.read_serial_data()

        if input1 and input2:
            processed_data = self.plot_manager.process_data(input1, input2)
            if processed_data:
                tmp1, tmp2, tmp3, tmp4, tmp5, tmp6 = processed_data
                if self.num == 0:
                    self.t0 = tmp6
                tmp6 -= self.t0
                self.plot_manager.update_arrays(tmp1, tmp2, tmp3,
                                                tmp4, tmp5, tmp6)
                if self.num % 5 == 0:
                    self.plot_manager.update_plts(tmp1, tmp2, tmp3,
                                                  tmp4, tmp5, tmp6)
        self.num += 1
        if self.num >= DATA_LENGTH:
            self.timer.stop()

    def exit_func(self):
        self.sm1.close_port()
        self.sm2.close_port()
        self.close()


class MultiAxisGraphWidget(pg.GraphicsLayoutWidget):
    def __init__(self):
        """コンストラクタ

        GraphicalLayoutWidgetを継承
        """
        super().__init__()
        self.show = True
        self.font = QFont(FONT_FAMILY, FONT_SIZE)

        self.plot1 = self.addPlot(row=0, col=0)
        self.curve1 = self.plot1.plot(pen=(221, 238, 255))

        self.curve2 = pg.PlotCurveItem(pen=(153, 221, 255))
        self.curve3 = pg.PlotCurveItem(pen=(181, 255, 20))
        self.curve4 = pg.PlotCurveItem(pen='r')
        self.curve5 = pg.PlotCurveItem(pen='y')

        self.view_box2 = pg.ViewBox()
        self.view_box3 = pg.ViewBox()
        self.view_box4 = pg.ViewBox()
        self.view_box5 = pg.ViewBox()

        self.view_box2.addItem(self.curve2)
        self.view_box3.addItem(self.curve3)
        self.view_box4.addItem(self.curve4)
        self.view_box5.addItem(self.curve5)

        self.ax5 = pg.AxisItem(orientation='right')
        self.set_graph_multiple_axis(
            self.plot1, self.view_box2, self.view_box3, self.view_box4,
            self.view_box5, self.ax5)
        self.set_graph_frame_font(self.plot1, self.ax5)
        self.setup_labels()

        pg.setConfigOptions(antialias=True)

    def set_graph_multiple_axis(self, plot1: pg.PlotItem,
                                view_box2:   pg.ViewBox,
                                view_box3:   pg.ViewBox,
                                view_box4:   pg.ViewBox,
                                view_box5:   pg.ViewBox = None,
                                ax5:         pg.AxisItem = None
                                ):
        plot1.showAxis('right')
        plot1.scene().addItem(view_box2)
        plot1.scene().addItem(view_box3)
        plot1.scene().addItem(view_box4)
        view_box3.linkView(1, view_box4)
        plot1.getAxis('left').linkToView(view_box2)
        plot1.getAxis('right').linkToView(view_box3)
        view_box2.setXLink(plot1)
        view_box2.setYLink(plot1)
        view_box3.setXLink(plot1)
        view_box4.setXLink(plot1)
        view_box2.sigRangeChanged.connect(
            lambda: view_box2.setGeometry(plot1.vb.sceneBoundingRect()))
        view_box3.sigRangeChanged.connect(
            lambda: view_box3.setGeometry(plot1.vb.sceneBoundingRect()))
        view_box4.sigRangeChanged.connect(
            lambda: view_box4.setGeometry(plot1.vb.sceneBoundingRect()))

        if view_box5 is not None and ax5 is not None:
            spacer = QGraphicsWidget()
            spacer.setMaximumSize(15, 15)
            plot1.layout.addItem(spacer, 2, 3)
            plot1.layout.addItem(ax5, 2, 4)
            plot1.scene().addItem(view_box5)
            ax5.linkToView(view_box5)
            view_box5.setXLink(plot1)
            view_box5.sigRangeChanged.connect(
                lambda: view_box5.setGeometry(plot1.vb.sceneBoundingRect()))

    def set_graph_frame_font(self, p1: pg.PlotItem, ax5: pg.AxisItem) -> None:
        p1.getAxis('bottom').setStyle(tickFont=self.font)
        p1.getAxis('bottom').setTextPen('#FFF')
        p1.getAxis('left').setStyle(tickFont=self.font)
        p1.getAxis('left').setTextPen('#FFF')
        p1.getAxis('right').setStyle(tickFont=self.font)
        p1.getAxis('right').setTextPen('#FFF')
        ax5.setStyle(tickFont=self.font)
        ax5.setTextPen('#FFF')
        p1.getAxis('bottom').setHeight(3.5 * 12)
        p1.getAxis('left').setWidth(4 * 12)
        p1.getAxis('right').setWidth(4.3 * 12)
        ax5.setWidth(6 * 12)

    def setup_labels(self) -> None:
        labelstyle = {'color': '#FFF', 'font-size': '12pt'}
        self.plot1.setLabel('left', FORCE_AX_LAVEL, **labelstyle)
        self.plot1.setLabel('right', DISP_AX_LAVEL, **labelstyle)
        self.plot1.setLabel('bottom', TIME_AX_LAVEL, **labelstyle)
        self.ax5.setLabel(SENSOR_AX_LAVEL, **labelstyle)

        self.plot1.setXRange(0, 50, padding=0)
        self.plot1.setYRange(-0.1, 3.3, padding=0)
        # p1.setRange(yRange = (-10, 10), padding = 0)
        self.view_box2.setRange(yRange=(-0.1, 3.3), padding=0)
        self.view_box3.setRange(yRange=(-10, 10), padding=0)
        self.view_box4.setRange(yRange=(-10, 10), padding=0)
        self.view_box5.setRange(yRange=(-0.1, 3.3), padding=0)


class PlotArrayHandler:
    """プロットマネージャ
    """
    def __init__(self, plot_widget: MultiAxisGraphWidget):
        """コンストラクタ

        Arguments:
            plot_widget -- プロットウィジェット
        """
        self.pw = plot_widget
        self.reset_data()

    def reset_data(self):
        self.t = np.array([])
        self.y1 = np.array([])
        self.y2 = np.array([])
        self.y3 = np.array([])
        self.y4 = np.array([])
        self.y5 = np.array([])

        self.t_plt = np.array([])
        self.y1_plt = np.array([])
        self.y2_plt = np.array([])
        self.y3_plt = np.array([])
        self.y4_plt = np.array([])
        self.y5_plt = np.array([])

    def process_data(self, input1, input2):
        """一時データの切り出しと加工"""
        try:
            tmp3, tmp4, tmp6 = input1.split(",")
            tmp5, tmp1, tmp2 = input2.split(",")
            tmp1 = float(tmp1) * 3.3 / 4095
            tmp2 = float(tmp2) * 3.3 / 4095
            tmp3 = float(tmp3)
            tmp4 = float(tmp4)
            tmp5 = float(tmp5) * 3.3 / 4095
            tmp6 = float(tmp6) / MICRO_TO_UNIT
            return tmp1, tmp2, tmp3, tmp4, tmp5, tmp6
        except ValueError:
            return None

    def update_arrays(self, tmp1, tmp2, tmp3, tmp4, tmp5, tmp6):
        """保存用配列に値を追加"""
        self.y1 = np.append(self.y1, tmp1)
        self.y2 = np.append(self.y2, tmp2)
        self.y3 = np.append(self.y3, tmp3)
        self.y4 = np.append(self.y4, tmp4)
        self.y5 = np.append(self.y5, tmp5)
        self.t = np.append(self.t, tmp6)

    def update_plts(self, tmp1, tmp2, tmp3, tmp4, tmp5, tmp6):
        """表示用配列に値を追加"""
        self.y1_plt = np.append(self.y1_plt, tmp1)
        self.y2_plt = np.append(self.y2_plt, tmp2)
        self.y3_plt = np.append(self.y3_plt, tmp3)
        self.y4_plt = np.append(self.y4_plt, tmp4)
        self.y5_plt = np.append(self.y5_plt, tmp5)
        self.t_plt = np.append(self.t_plt, tmp6)
        self.pw.curve1.setData(self.t_plt, self.y1_plt)
        self.pw.curve2.setData(self.t_plt, self.y2_plt)
        self.pw.curve3.setData(self.t_plt, self.y3_plt)
        self.pw.curve4.setData(self.t_plt, self.y4_plt)
        self.pw.curve5.setData(self.t_plt, self.y5_plt)


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
        self.sm.write(MOTOR_X_START)

    def stop_motor_x(self):
        """X軸モーターを停止する"""
        self.sm.write(MOTOR_X_STOP)

    def reverse_motor_x(self):
        """X軸モーターの回転を反転する"""
        self.sm.write(MOTOR_X_REVERSE)
        self.on_motor_x_reversed.emit()

    def start_motor_y(self):
        """Y軸モーターを開始する"""
        self.sm.write(MOTOR_Y_START)

    def stop_motor_y(self):
        """Y軸モーターを停止する"""
        self.sm.write(MOTOR_Y_STOP)

    def reverse_motor_y(self):
        """Y軸モーターの回転を反転する"""
        self.sm.write(MOTOR_Y_REVERSE)
        self.on_motor_y_reversed.emit()


class MotorControlWidget(QWidget):
    """モーターコントロールウィジェット"""
    def __init__(self, motor_controller):
        """コンストラクタ

        Arguments:
            motor_controller -- MotorControllerオブジェクト
        """
        super().__init__()
        self.motor_controller = motor_controller
        self.init_ui()
        self.init_signals()

    def init_ui(self):
        """UIの初期化"""
        layout = QGridLayout(self)

        self.motor_start_1 = create_btn(
            ELONG_X_LAVEL, self.motor_controller.start_motor_x)
        self.motor_stop_1 = create_btn(
            SHRINK_X_LAVEL, self.motor_controller.stop_motor_x)
        self.motor_reverse_1 = create_btn(
            REVERS_X_LAVEL, self.motor_controller.reverse_motor_x)
        self.motor_start_2 = create_btn(
            ELONG_Y_LAVEL, self.motor_controller.start_motor_y)
        self.motor_stop_2 = create_btn(
            SHRINK_Y_LAVEL, self.motor_controller.stop_motor_y)
        self.motor_reverse_2 = create_btn(
            REVERS_Y_LAVEL, self.motor_controller.reverse_motor_y)

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
                                ELONG_X_LAVEL, SHRINK_X_LAVEL)

    def on_motor_y_reversed(self):
        """motor_y_reversedに対するスロットメソッド"""
        self.toggle_button_text(self.motor_start_2,
                                ELONG_Y_LAVEL, SHRINK_Y_LAVEL)

    def toggle_button_text(self, button, text1, text2):
        """ボタンのテキストを切り替える"""
        button.setText(text2 if button.text() == text1 else text1)


def create_btn(text, callback, is_enable=True):
    """ボタンを生成する関数

    Arguments:
        text -- ボタンテキスト
        callback -- コールバック関数

    Keyword Arguments:
        enabled -- 押下可否 (default: {True})

    Returns:
        QPushButton ボタンオブジェクト
    """
    button = QPushButton(text)
    button.clicked.connect(callback)
    button.setEnabled(is_enable)
    return button


def main():
    """メイン関数
    """
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
