from PyQt6.QtWidgets import (QMainWindow, QPushButton, QWidget, QLineEdit,
                             QGridLayout, QApplication, QGraphicsWidget,
                             QLabel, QRadioButton)
import sys
import numpy as np
import serial
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import pandas as pd
import datetime
import serial.tools.list_ports

# インスタンス変数　オブジェクトごとに違う値をとる。
# クラス変数　オブジェクト同士で共通の値をとる。
# 両方，クラスの中からは，self.変数名でアクセスできる。
# メソッドの中の一時的な変数

# カレントディレクトリは(jupyter)の仮想環境が動いているディレクトリなので注意

#  コマンド
#  0 計測開始
#  1 計測終了
#  2 なし
#  3 モーター①スタート
#  4 モーター①ストップ
#  5 モーター①逆回転
#  6 なし
#  7 モーター②スタート
#  8 モーター②ストップ
#  9 モーター②逆回転


class Window(QMainWindow):

    MICRO_TO_UNIT = 1000000  # μ秒から秒に行く定数
    DATA_LENGTH = int(2**20)  # 最大のデータ長
    BAUDRATE = 115200  # USBシリアルのボーレート。最大115200
    style = """
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
    style_reject = """
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

    # たぶんmicrosがオーバーフローするところまでのデータ長にしておけばいい

    def __init__(self):
        super().__init__()  # ok

        # ウィンドウの設定
        self.setWindowTitle("KES-F System")  # ok
        self.setGeometry(100, 100, 800, 450)  # ok

        # ウィジェット・レイアウト
        self.widget = QWidget()  # ok
        self.widget_for_time_series = pg.GraphicsLayoutWidget(show=True)  # ok plot_widgetに改名
        self.widget_for_comport = QWidget()  # ok
        self.widget_for_controller = QWidget()  # ok

        self.setCentralWidget(self.widget)  # ok

        self.widget_for_time_series.setMinimumSize(800, 450)  # ok

        self.layout = QGridLayout()  # ok
        self.widget.setLayout(self.layout)  # ok

        self.layout2 = QGridLayout()  # ok
        self.widget_for_comport.setLayout(self.layout2)  # ok

        self.layout3 = QGridLayout()  # ok
        self.widget_for_controller.setLayout(self.layout3)  # ok

        self.UiComponents()  # Uiの要素を表示する
        self.plot_with_respect_to_time()  # ! 不明

        self.layout.addWidget(self.widget_for_time_series, 0, 1)  # ok
        self.layout.addWidget(self.widget_for_comport, 0, 0)  # ok

        self.layout.addWidget(self.save, 2, 0)  # ok
        self.layout.addWidget(self.plot_start, 3, 0)  # ok
        self.layout.addWidget(self.plot_stop, 4, 0)  # ok
        self.layout.addWidget(self.re_start, 5, 0)  # ok
        self.layout.addWidget(self.exit, 6, 0)  # ok

        self.layout.addWidget(self.widget_for_controller, 2, 1, 4, 1)  # ok

        self.layout.addWidget(self.line, 2, 1)  # ok

        self.layout3.addWidget(self.motor_start_1, 0, 0)  # ok
        self.layout3.addWidget(self.motor_stop_1, 0, 1)  # ok
        self.layout3.addWidget(self.motor_reverse_1, 0, 2)  # ok

        self.layout3.addWidget(self.motor_start_2, 1, 0)  # ok
        self.layout3.addWidget(self.motor_stop_2, 1, 1)  # ok
        self.layout3.addWidget(self.motor_reverse_2, 1, 2)  # ok

        self.layout.addWidget(self.message_box, 6, 1)  # ok

        self.show()  # ok

    def UiComponents(self):
        self.save = Button('save', self.save_func)  # ok

        self.plot_start = Button('start', self.plot_start_func, False)  # ok

        self.plot_stop = Button('stop', self.plot_stop_func, False)  # ok

        self.re_start = Button('re start', self.re_start_func, False)  # ok

        self.exit = Button('exit', self.exit_meth)  # ok

        self.motor_start_1 = Button('Xのばす', self.motor_start_func_1)  # ok

        self.motor_stop_1 = Button('Xとめる', self.motor_stop_func_1)  # ok

        self.motor_reverse_1 = Button('X逆回転', self.counter_rotate_1)  # ok

        self.motor_start_2 = Button('Yのばす', self.motor_start_func_2)  # ok

        self.motor_stop_2 = Button('Yとめる', self.motor_stop_func_2)  # ok

        self.motor_reverse_2 = Button('Y逆回転', self.counter_rotate_2)  # ok

        dt = datetime.datetime.now()  # ok
        line_text = dt.strftime('%Y-%m%d-%H%M-プロジェクト名')  # ok
        self.line = QLineEdit(line_text)  # ok
        self.line.setFont(QtGui.QFont('Yu Gothic UI', 10))  # ok

        self.message_box = QLabel('シリアルポートを選択してください')  # ok

        self.select_comport(self.onClickedRadioButton)
        self.select_comport_2nd(self.onClickedRadioButton_2nd)

    def save_func(self):  # ! 保存関数がどうなったか？
        array = []
        array = np.append(self.t, self.y1)
        array = np.append(array, self.y2)
        array = np.append(array, self.y3)
        array = np.append(array, self.y4)
        array = np.append(array, self.y5)
        array = np.reshape(array, (6, len(self.t)))  # 6行×(サンプル数)列のarrayに整形
        array = np.transpose(array)  # 転置する->(サンプル数)行×5
        data = pd.DataFrame(
            array, columns=['Time', 'F1', 'F2', 'Disp1', 'Disp2', 'Sensor'])
        data.to_csv(str(self.line.text()) + '.csv')

    def plot_start_func(self):  # プロットのスタート関数
        self.wait_time = 0  # 下記
        self.plot_stop.setEnabled(True)  # ok
        try:
            self.ser.write(b'0')  # ok
            self.plot_start.setStyleSheet("")  # ok
            self.plot_start.setText('・・・')  # ok
            self.plot_stop.setStyleSheet(self.style_reject)  # ok
        except Exception:
            self.plot_start.setText('エラー！')    # ok
        self.timer = QtCore.QTimer()  # ok
        self.timer.timeout.connect(self.update)  # ok
        self.t = np.array([])  # ok 上に移動した
        self.y1 = np.array([])
        self.y2 = np.array([])
        self.y3 = np.array([])
        self.y4 = np.array([])
        self.y5 = np.array([])

        self.t_plt = np.array([]) # ! pltがなくなった
        self.y1_plt = np.array([])
        self.y2_plt = np.array([])
        self.y3_plt = np.array([])
        self.y4_plt = np.array([])
        self.y5_plt = np.array([])
        self.timer.start(self.wait_time)  # 解決

    def plot_stop_func(self):
        self.timer.stop()  # ok
        self.plot_stop.setEnabled(False)  # ok
        self.plot_stop.setStyleSheet("")  # ok
        self.ser.write(b'1')  # ok
        self.re_start.setEnabled(True)  # ok
        self.re_start.setStyleSheet(self.style)  # ok
        # ここでは，シリアルをcloseしない。

    def re_start_func(self):
        self.timer.stop()  # !

        self.num = 0  # !

        self.t = np.array([])  # ok
        self.y1 = np.array([])
        self.y2 = np.array([])
        self.y3 = np.array([])
        self.y4 = np.array([])
        self.y5 = np.array([])

        self.t_plt = np.array([])  # !
        self.y1_plt = np.array([])
        self.y2_plt = np.array([])
        self.y3_plt = np.array([])
        self.y4_plt = np.array([])
        self.y5_plt = np.array([])

        self.curve.setData(self.t, self.y1_plt)  # !
        self.curve2.setData(self.t, self.y2_plt)
        self.curve3.setData(self.t, self.y3_plt)
        self.curve4.setData(self.t, self.y4_plt)
        self.curve5.setData(self.t, self.y5_plt)

        self.plot_start_func()  # !

        self.re_start.setStyleSheet("")  # !

    #  ok
    def motor_start_func_1(self):
        self.ser.write(b'3')

    def motor_stop_func_1(self):
        self.ser.write(b'4')

    def counter_rotate_1(self):
        self.ser.write(b'5')
        if self.motor_start_1.text() == 'Xのばす':
            self.motor_start_1.setText('X縮める')
        else:
            self.motor_start_1.setText('Xのばす')

    def motor_start_func_2(self):
        self.ser.write(b'7')

    def motor_stop_func_2(self):
        self.ser.write(b'8')

    def counter_rotate_2(self):
        self.ser.write(b'9')
        if self.motor_start_2.text() == 'Yのばす':
            self.motor_start_2.setText('Y縮める')
        else:
            self.motor_start_2.setText('Yのばす')
    # ここまで

    def com_port_func(self):  # ok
        ports = list(serial.tools.list_ports.comports())
        portNames = []
        for ps in ports:
            portNow = ps.device
            portNames.append(portNow)
        return portNames

    def select_comport(self, fun):  # ok
        portNames = self.com_port_func()
        i = 0
        for p in portNames:
            btntmp = QRadioButton(p)
            btntmp.com = p  # ボタンの.comというプロパティにCOMポート名を持たせる
            btntmp.released.connect(fun)
            self.layout2.addWidget(btntmp, i, 0)
            i = i + 1

    def select_comport_2nd(self, fun):  # ! 2つめ
        portNames = self.com_port_func()
        i = 0
        for p in portNames:
            btntmp = QRadioButton(p)
            btntmp.com = p
            btntmp.released.connect(fun)
            self.layout2.addWidget(btntmp, i, 1)
            i = i + 1

    def onClickedRadioButton(self):  # ok
        radio_clicked_now = self.widget_for_comport.sender(
        )
        self.comport = radio_clicked_now.com
        self.plot_start.setEnabled(True)
        self.plot_start.setStyleSheet(self.style)
        self.open_and_check_serial(
            self.comport)
        return self.comport

    def open_and_check_serial(self, comport):  # ok
        try:
            self.ser = serial.Serial(
                comport, self.BAUDRATE)
            self.message_box.setText('シリアルポートを開きました')
        except Exception as e:
            self.message_box.setText(str(e))

    def onClickedRadioButton_2nd(self):  # ! 2つめ
        radio_clicked_now = self.widget_for_comport.sender()
        self.comport_2nd = radio_clicked_now.com
        self.plot_start.setEnabled(True)
        self.plot_start.setStyleSheet(self.style)
        self.open_and_check_serial_2nd(
            self.comport_2nd)
        return self.comport_2nd

    def open_and_check_serial_2nd(self, comport):  # ! 2つめ
        try:
            self.ser_2nd = serial.Serial(
                comport, self.BAUDRATE)
            self.message_box.setText('2つめのシリアルポートも開きました')
        except Exception as e:
            self.message_box.setText(str(e))

    def setGraphMultipleAxis(self, p1, p2, p3, p4, p5, ax5):
        p1.showAxis('right')  # ok
        p1.scene().addItem(p2)  # ok
        p1.scene().addItem(p3)  # ok
        p1.scene().addItem(p4)  # ok
        p3.linkView(1, p4)  # ok
        p1.getAxis('left').linkToView(p2)  # ok
        p1.getAxis('right').linkToView(p3)  # ok
        p2.setXLink(p1)  # ok
        p2.setYLink(p1)  # ok
        p3.setXLink(p1)  # ok
        p4.setXLink(p1)  # ok
        p2.sigRangeChanged.connect(
            lambda: p2.setGeometry(p1.vb.sceneBoundingRect()))  # ok
        p3.sigRangeChanged.connect(
            lambda: p3.setGeometry(p1.vb.sceneBoundingRect()))  # ok
        p4.sigRangeChanged.connect(
            lambda: p4.setGeometry(p1.vb.sceneBoundingRect()))  # ok

        if p5 is not None and ax5 is not None:
            spacer = QGraphicsWidget()  # ok
            spacer.setMaximumSize(15, 15)  # ok
            p1.layout.addItem(spacer, 2, 3)  # ok

            p1.layout.addItem(ax5, 2, 4)  # ok
            p1.scene().addItem(p5)  # ok
            ax5.linkToView(p5)  # ok
            p5.setXLink(p1)  # ok

            p5.sigRangeChanged.connect(
                lambda: p5.setGeometry(p1.vb.sceneBoundingRect()))  # ok

    def setGraphFrameFont(self, p1, ax5):
        self.font = QtGui.QFont()  # ok
        self.font.setPointSize(12)  # ok
        self.fontFamily = 'Yu Gothic UI'  # ok
        self.font.setFamily(self.fontFamily)  # ok
        p1.getAxis('bottom').setStyle(tickFont=self.font)  # ok
        p1.getAxis('bottom').setTextPen('#FFF')  # ok
        p1.getAxis('left').setStyle(tickFont=self.font)  # ok
        p1.getAxis('left').setTextPen('#FFF')  # ok
        p1.getAxis('right').setStyle(tickFont=self.font)  # ok
        p1.getAxis('right').setTextPen('#FFF')  # ok
        ax5.setStyle(tickFont=self.font)  # ok
        ax5.setTextPen('#FFF')  # ok
        p1.getAxis('bottom').setHeight(3.5 * 12)  # ok
        p1.getAxis('left').setWidth(4 * 12)  # ok
        p1.getAxis('right').setWidth(4.3 * 12)  # ok
        ax5.setWidth(6 * 12)  # ok

    def plot_with_respect_to_time(self):
        # plotItem
        graph1 = self.widget_for_time_series.addPlot(row=0, col=0)  # ok
        graph2 = pg.PlotCurveItem(title="Force2", pen=(153, 221, 255))  # ok
        p2 = pg.ViewBox()  # ok
        p2.addItem(graph2)  # ok 以下同じ
        graph3 = pg.PlotCurveItem(title="Disp1", pen=(181, 255, 20))
        p3 = pg.ViewBox()
        p3.addItem(graph3)
        graph4 = pg.PlotCurveItem(title="Disp2", pen='r')
        p4 = pg.ViewBox()
        p4.addItem(graph4)
        graph5 = pg.PlotCurveItem(title="Sensor", pen='y')
        p5 = pg.ViewBox()
        p5.addItem(graph5)
        ax5 = pg.AxisItem(orientation='right')  # ここまで
        self.setGraphMultipleAxis(graph1, p2, p3, p4, p5, ax5)  # ok
        self.setGraphFrameFont(graph1, ax5)

        label = f'<font face={self.fontFamily}>Time / s</font>'
        label1 = f'<font face={self.fontFamily}>Force / N</font>'
        label2 = f'<font face={self.fontFamily}>Displacement / mm</font>'
        label3 = f'<font face={self.fontFamily}>Sensor Output / V</font>'

        labelstyle = {'color': '#FFF', 'font-size': '12pt'}

        graph1.setLabel('left', label1, **labelstyle)
        graph1.setLabel('right', label2, **labelstyle)
        graph1.setLabel('bottom', label, **labelstyle)
        ax5.setLabel(label3, **labelstyle)

        # ok
        graph1.setXRange(0, 50, padding=0)
        graph1.setYRange(-0.1, 3.3, padding=0)
        # p1.setRange(yRange = (-10, 10), padding = 0)
        p2.setRange(yRange=(-0.1, 3.3), padding=0)
        p3.setRange(yRange=(-10, 10), padding=0)
        p4.setRange(yRange=(-10, 10), padding=0)
        p5.setRange(yRange=(-0.1, 3.3), padding=0)
        # ここまで

        self.num = 0  # !グラフウィジェトにはこれを持たせない

        # 適当なyデータ
        self.t = np.array([])
        self.y1 = np.array([])
        self.y2 = np.array([])
        self.y3 = np.array([])
        self.y4 = np.array([])
        self.y5 = np.array([])

        # 適当なyデータ
        self.t_plt = np.array([])
        self.y1_plt = np.array([])
        self.y2_plt = np.array([])
        self.y3_plt = np.array([])
        self.y4_plt = np.array([])
        self.y5_plt = np.array([])  # !ここまで

        self.curve = graph1.plot(pen=(221, 238, 255))  # ok
        self.curve2 = graph2  # ?不要?
        self.curve3 = graph3
        self.curve4 = graph4
        self.curve5 = graph5
        pg.setConfigOptions(antialias=True)  # ok

        # self.widget_for_comport.setStyleSheet("background-color:red;")

    def update(self):
        if self.num == 0:
            input_serial = self.ser.readline().rstrip()
            input_serial_2nd = self.ser_2nd.readline().rstrip()
            try:
                input = input_serial.decode()
                input_2nd = input_serial_2nd.decode()
                tmp3, tmp4, tmp6 = input.split(",")
                tmp5, tmp1, tmp2 = input_2nd.split(",")
                tmp1 = float(tmp1) * 3.3 / 4095
                tmp2 = float(tmp2) * 3.3 / 4095
                tmp3 = float(tmp3)
                tmp4 = float(tmp4)
                tmp5 = float(tmp5) * 3.3 / 4095
                tmp6 = float(tmp6) / self.MICRO_TO_UNIT
                self.t0 = tmp6
                self.y1 = np.append(self.y1, tmp1)
                self.y2 = np.append(self.y2, tmp2)
                self.y3 = np.append(self.y3, tmp3)
                self.y4 = np.append(self.y4, tmp4)
                self.y5 = np.append(self.y5, tmp5)
                self.t = np.append(self.t, 0)
                self.y1_plt = np.append(self.y1_plt, tmp1)
                self.y2_plt = np.append(self.y2_plt, tmp2)
                self.y3_plt = np.append(self.y3_plt, tmp3)
                self.y4_plt = np.append(self.y4_plt, tmp4)
                self.y5_plt = np.append(self.y5_plt, tmp5)
                self.t_plt = np.append(self.t_plt, 0)
                self.curve.setData(self.t_plt, self.y1_plt)
                self.curve2.setData(self.t_plt, self.y2_plt)
                self.curve3.setData(self.t_plt, self.y3_plt)
                self.curve4.setData(self.t_plt, self.y4_plt)
                self.curve5.setData(self.t_plt, self.y5_plt)
                self.num += 1
            except (ValueError, UnicodeDecodeError):
                self.num += 1
        elif 0 < self.num < self.DATA_LENGTH:
            input_serial = self.ser.readline().rstrip()
            input_serial_2nd = self.ser_2nd.readline().rstrip()
            try:
                input = input_serial.decode()
                input_2nd = input_serial_2nd.decode()
                tmp3, tmp4, tmp6 = input.split(",")
                tmp5, tmp1, tmp2 = input_2nd.split(",")
                tmp1 = float(tmp1) * 3.3 / 4095
                tmp2 = float(tmp2) * 3.3 / 4095
                tmp3 = float(tmp3)
                tmp4 = float(tmp4)
                tmp5 = float(tmp5) * 3.3 / 4095
                tmp6 = float(tmp6) / self.MICRO_TO_UNIT - self.t0
                self.y1 = np.append(self.y1, tmp1)
                self.y2 = np.append(self.y2, tmp2)
                self.y3 = np.append(self.y3, tmp3)
                self.y4 = np.append(self.y4, tmp4)
                self.y5 = np.append(self.y5, tmp5)
                self.t = np.append(self.t, tmp6)
                if self.num % 5 == 0:  #50 Hzで表示
                    self.y1_plt = np.append(self.y1_plt, tmp1)
                    self.y2_plt = np.append(self.y2_plt, tmp2)
                    self.y3_plt = np.append(self.y3_plt, tmp3)
                    self.y4_plt = np.append(self.y4_plt, tmp4)
                    self.y5_plt = np.append(self.y5_plt, tmp5)
                    self.t_plt = np.append(self.t_plt, tmp6)
                    self.curve.setData(self.t_plt, self.y1_plt)
                    self.curve2.setData(self.t_plt, self.y2_plt)
                    self.curve3.setData(self.t_plt, self.y3_plt)
                    self.curve4.setData(self.t_plt, self.y4_plt)
                    self.curve5.setData(self.t_plt, self.y5_plt)
                self.num += 1
            except (ValueError, UnicodeDecodeError):
                self.num += 1
        else:
            self.timer.stop()

    def exit_meth(self):  # たぶんok
        try:
            self.timer.stop()
            self.ser.close()
        except Exception:
            pass
        finally:
            sys.exit(App.exec())


class Button(QPushButton):  # メソッドに移動 ok

    def __init__(self, text, func, is_enabled=True):
        super().__init__(None)

        self.setText(text)
        self.setFixedSize(120, 40)
        self.clicked.connect(func)

        btn_font = QtGui.QFont()
        btn_font.setFamily('Yu Gothic UI')
        btn_font.setPointSize(12)
        self.setFont(btn_font)

        self.setEnabled(is_enabled)


# PyQT6のアプリケーションオブジェクト
App = QApplication(sys.argv)  # ok
# インスタンス生成
window = Window()  # ok
# スタートさせる??
sys.exit(App.exec())  # ok
  # ok