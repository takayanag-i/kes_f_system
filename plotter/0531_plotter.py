import sys
import datetime

from PyQt6.QtWidgets import (QMainWindow, QPushButton, QWidget,
                             QGraphicsWidget, QLineEdit, QGridLayout,
                             QApplication, QLabel, QComboBox)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QTimer
import numpy as np
import serial
import pyqtgraph as pg
import pandas as pd
import serial.tools.list_ports


MICRO_TO_UNIT = 1000000
DATA_LENGTH = int(2**20)
BAUDRATE = 115200
PLOT_START = b'0'
PLOT_STOP = b'1'

MOTOR_X_START = b'3'
MOTOR_X_STOP = b'4'
MOTOR_X_REVERSE = b'5'

MOTOR_Y_START = b'7'
MOTOR_Y_STOP = b'8'
MOTOR_Y_REVERSE = b'9'

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
            baudrate -- ボーレート 整数
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

    def read_line(self):
        """シリアルから読む.

        文字列の右側の空白を削除

        Returns:
        """
        if self.ser and self.ser.is_open:
            return self.ser.readline().decode('utf-8').strip()
        return None


class MotorController:
    """モーターコントロール
    """
    def __init__(self, serial_manager):
        self.serial_manager = serial_manager

    def start_motor_x(self):
        self.serial_manager.write(MOTOR_X_START)
        print("Motor x started")

    def stop_motor_x(self):
        self.serial_manager.write(MOTOR_X_STOP)
        print("Motor x stopped")

    def reverse_motor_x(self):
        self.serial_manager.write(MOTOR_X_REVERSE)
        if self.motor_start_1.text() == 'Xのばす':
            self.motor_start_1.setText('X縮める')
        else:
            self.motor_start_1.setText('Xのばす')
        print("Motor x reversed")

    def start_motor_y(self):
        self.serial_manager.write(MOTOR_Y_START)
        print("Motor x started")

    def stop_motor_y(self):
        self.serial_manager.write(MOTOR_Y_STOP)
        print("Motor x stopped")

    def reverse_motor_y(self):
        self.serial_manager.write(MOTOR_Y_REVERSE)
        if self.motor_start_2.text() == 'Yのばす':
            self.motor_start_2.setText('Y縮める')
        else:
            self.motor_start_2.setText('Yのばす')
        print("Motor x reversed")


class PlotManager:
    def __init__(self, plot_widget):
        """コンストラクタ

        Arguments:
            plot_widget -- プロットウィジェット
        """
        self.plot_widget = plot_widget
        self.init_plot()
        self.reset_data()

    def init_plot(self):
        pass
        # self.plot = self.plot_widget.addPlot()
        # self.plot.showGrid(x=True, y=True)
        # self.plot.addLegend()
        # self.curve1 = self.plot.plot(pen='r', name='F1')
        # self.curve2 = self.plot.plot(pen='g', name='F2')
        # self.curve3 = self.plot.plot(pen='b', name='Disp1')
        # self.curve4 = self.plot.plot(pen='y', name='Disp2')
        # self.curve5 = self.plot.plot(pen='m', name='Sensor')

    def reset_data(self):
        self.t = np.array([])
        self.y1 = np.array([])
        self.y2 = np.array([])
        self.y3 = np.array([])
        self.y4 = np.array([])
        self.y5 = np.array([])

    def update_plot(self, new_data):
        self.t = np.append(self.t, new_data['t'])
        self.y1 = np.append(self.y1, new_data['y1'])
        self.y2 = np.append(self.y2, new_data['y2'])
        self.y3 = np.append(self.y3, new_data['y3'])
        self.y4 = np.append(self.y4, new_data['y4'])
        self.y5 = np.append(self.y5, new_data['y5'])

        self.curve1.setData(self.t, self.y1)
        self.curve2.setData(self.t, self.y2)
        self.curve3.setData(self.t, self.y3)
        self.curve4.setData(self.t, self.y4)
        self.curve5.setData(self.t, self.y5)


class Window(QMainWindow):
    """メインウィンドウクラス

    Arguments:
        QMainWindow -- 親クラス
    """
    def __init__(self):
        super().__init__()
        self.serial_manager = SerialManager()  # シリアルマネージャのnew
        # モータコントローラのnew
        self.motor_controller = MotorController(self.serial_manager)
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
        # self.show()

    def create_widgets(self):
        """ウィジェットの生成
        """
        self.plot_widget = MultiAxisGraphWidget()
        self.plot_widget.setMinimumSize(800, 450)
        self.plot_manager = PlotManager(self.plot_widget)  # ? プロットマネージャのnew

        self.widget_for_comport = QWidget()
        self.layout2 = QGridLayout()
        self.widget_for_comport.setLayout(self.layout2)

        self.widget_for_controller = QWidget()
        self.layout3 = QGridLayout()
        self.widget_for_controller.setLayout(self.layout3)

        self.save_button = self.create_button('Save', self.save_func)
        self.plot_start_button = self.create_button(
            'Start', self.plot_start_func, False
        )
        self.plot_stop_button = self.create_button(
            'Stop', self.plot_stop_func, False
        )
        self.restart_button = self.create_button(
            'Reset', self.reset_func, False
        )
        self.exit_button = self.create_button('Exit', self.exit_func)

        self.motor_start_1 = self.create_button(
            'Xのばす', lambda: self.motor_controller.start_motor_x
        )
        self.motor_stop_1 = self.create_button(
            'Xとめる', lambda: self.motor_controller.stop_motor_x
        )
        self.motor_reverse_1 = self.create_button(
            'X逆回転', lambda: self.motor_controller.reverse_motor_x
        )

        self.motor_start_2 = self.create_button(
            'Yのばす', lambda: self.motor_controller.start_motor_y
        )
        self.motor_stop_2 = self.create_button(
            'Yとめる', lambda: self.motor_controller.stop_motor_y
        )
        self.motor_reverse_2 = self.create_button(
            'Y逆回転', lambda: self.motor_controller.reverse_motor_y
        )

        dt = datetime.datetime.now()
        line_text = dt.strftime('%Y-%m%d-%H%M-プロジェクト名')
        self.line_edit = QLineEdit(line_text)
        self.line_edit.setFont(QFont('Yu Gothic UI', 10))

        self.message_box = QLabel('シリアルポートを選択してください')

        self.combobox = QComboBox()
        self.combobox.addItems(self.get_serial_ports())
        self.combobox.currentIndexChanged.connect(self.on_combobox_changed)

    def create_button(self, text, callback, is_enable=True):
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
        self.layout.addWidget(self.restart_button, 5, 0)
        self.layout.addWidget(self.exit_button, 6, 0)
        # コンボボックス
        self.layout2.addWidget(self.combobox, 0, 0)
        # テキストエリア
        self.layout.addWidget(self.line_edit, 2, 1)
        self.layout.addWidget(self.message_box, 6, 1)
        # コントローラ
        self.layout.addWidget(self.widget_for_controller, 2, 1, 4, 1)

        # コントローラへの追加
        self.layout3.addWidget(self.motor_start_1, 0, 0)
        self.layout3.addWidget(self.motor_stop_1, 0, 1)
        self.layout3.addWidget(self.motor_reverse_1, 0, 2)
        self.layout3.addWidget(self.motor_start_2, 1, 0)
        self.layout3.addWidget(self.motor_stop_2, 1, 1)
        self.layout3.addWidget(self.motor_reverse_2, 1, 2)

    def get_serial_ports(self):
        """接続可能なポート名を取得する

        Returns:
            ポート名のリスト
        """
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def on_combobox_changed(self, index):
        port_name = self.combobox.itemText(index)
        self.serial_manager.close_port()
        self.serial_manager.open_port(port_name)
        if self.serial_manager.ser.is_open:
            self.message_box.setText(f"Connected to {port_name}")
            self.plot_start_button.setEnabled(True)
            self.plot_start_button.setStyleSheet(STYLE)
        else:
            self.message_box.setText(f"Failed to connect to {port_name}")

    def save_func(self):
        array = np.append(np.array([self.plot_manager.t,
                                    self.plot_manager.y1, self.plot_manager.y2, self.plot_manager.y3, self.plot_manager.y4, self.plot_manager.y5]), axis=0)
        array = array.T
        columns = ['Time', 'F1', 'F2', 'Disp1', 'Disp2', 'Sensor']
        data = pd.DataFrame(array, columns=columns)
        data.to_csv(f"{self.line_edit.text()}.csv", index=False)

    def plot_start_func(self):
        self.plot_manager.reset_data()
        self.plot_stop_button.setEnabled(True)
        try:
            self.serial_manager.write(PLOT_START)
            self.plot_start_button.setStyleSheet("")
            self.plot_start_button.setText('・・・')
            self.plot_stop_button.setStyleSheet(STYLE_REJECT)
        except Exception:
            self.plot_start_button.setText('エラー！')
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(0)

    def plot_stop_func(self):
        self.timer.stop()
        self.plot_stop_button.setEnabled(False)
        self.plot_stop_button.setStyleSheet("")
        self.serial_manager.write(PLOT_STOP)
        self.restart_button.setEnabled(True)
        self.restart_button.setStyleSheet(STYLE)

    def reset_func(self):
        self.plot_manager.reset_data()
        self.plot_stop_button.setEnabled(False)
        self.plot_start_button.setEnabled(True)
        self.plot_start_button.setStyleSheet(STYLE)
        # !

    def update_plot(self):
        line = self.serial_manager.read_line()
        if line:
            data = self.parse_serial_data(line)
            self.plot_manager.update_plot(data)

    def parse_serial_data(self, line):
        try:
            parts = list(map(float, line.split(',')))
            return {
                't': parts[0],
                'y1': parts[1],
                'y2': parts[2],
                'y3': parts[3],
                'y4': parts[4],
                'y5': parts[5],
            }
        except ValueError:
            return None

    def exit_func(self):
        self.serial_manager.close_port()
        self.close()


class MultiAxisGraphWidget(pg.GraphicsLayoutWidget):
    def __init__(self):
        super().__init__()
        self.show = True
        self.fontFamily = 'Yu Gothic UI'
        self.font = QFont(self.fontFamily, 12)

        self.plot1 = self.addPlot(row=0, col=0)

        self.PlotCurve2 = pg.PlotCurveItem(title="Force2", pen=(153, 221, 255))
        self.p2 = pg.ViewBox()
        self.p2.addItem(self.PlotCurve2)
        self.PlotCurve3 = pg.PlotCurveItem(title="Disp1", pen=(181, 255, 20))
        self.p3 = pg.ViewBox()
        self.p3.addItem(self.PlotCurve3)
        self.PlotCurve4 = pg.PlotCurveItem(title="Disp2", pen='r')
        self.p4 = pg.ViewBox()
        self.p4.addItem(self.PlotCurve4)
        self.PlotCurve5 = pg.PlotCurveItem(title="Sensor", pen='y')
        self.p5 = pg.ViewBox()
        self.p5.addItem(self.PlotCurve5)
        self.ax5 = pg.AxisItem(orientation='right')

        self.set_graph_multiple_axis(
            self.plot1, self.p2, self.p3, self.p4, self.p5, self.ax5)
        self.set_graph_frame_font(self.plot1, self.ax5)
        self.setup_labels()

        self.curve = self.plot1.plot(pen=(221, 238, 255))
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
        label = f'<font face={self.fontFamily}>Time / s</font>'
        label1 = f'<font face={self.fontFamily}>Force / N</font>'
        label2 = f'<font face={self.fontFamily}>Displacement / mm</font>'
        label3 = f'<font face={self.fontFamily}>Sensor Output / V</font>'

        labelstyle = {'color': '#FFF', 'font-size': '12pt'}
        self.plot1.setLabel('left', label1, **labelstyle)
        self.plot1.setLabel('right', label2, **labelstyle)
        self.plot1.setLabel('bottom', label, **labelstyle)
        self.ax5.setLabel(label3, **labelstyle)

        self.plot1.setXRange(0, 50, padding=0)
        self.plot1.setYRange(-0.1, 3.3, padding=0)
        # p1.setRange(yRange = (-10, 10), padding = 0)
        self.p2.setRange(yRange=(-0.1, 3.3), padding=0)
        self.p3.setRange(yRange=(-10, 10), padding=0)
        self.p4.setRange(yRange=(-10, 10), padding=0)
        self.p5.setRange(yRange=(-0.1, 3.3), padding=0)


def main():
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
