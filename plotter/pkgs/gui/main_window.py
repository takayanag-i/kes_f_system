import datetime as dt

import serial.tools.list_ports
from PyQt6.QtWidgets import (QMainWindow, QWidget, QLineEdit,
                             QGridLayout, QLabel, QComboBox)
from PyQt6.QtGui import QFont

from ..common.button import Button
from ..common.constants import (Formats as fmt, FontConfig as fnt)
from ..gui.multi_axis_graph import MultiAxisGraphWidget
from ..gui.motor_ctrl_widget import MotorControlWidget


class Window(QMainWindow):
    """メインウィンドウクラス

    @Override QMainWindow
    """
    def __init__(self):
        super().__init__()
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
        self.widget_for_controller = MotorControlWidget()

        # ボタン
        self.save_button = Button('Save')
        self.plot_start_button = Button('Start', False)
        self.plot_stop_button = Button('Stop', False)
        self.plot_reset_button = Button('Reset', False)
        self.exit_button = Button('Exit')

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
        self.combobox1.addItems(self.get_serial_ports())
        self.combobox1_label = QLabel('COM Port : ESP32 Dev Module')

        self.combobox2.addItems(self.get_serial_ports())
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

    def get_serial_ports(self):
        """接続可能なポート名を取得する

        Returns:
            ポート名のリスト
        """
        ports = serial.tools.list_ports.comports()
        port_list = [port.device for port in ports]
        port_list.insert(0, '---')
        return port_list
