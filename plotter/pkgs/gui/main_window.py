import datetime as dt
import serial.tools.list_ports
from PyQt6.QtWidgets import (QMainWindow, QWidget, QLineEdit,
                             QGridLayout, QLabel, QComboBox)
from PyQt6.QtGui import QFont

from pkgs.common.constants import (Formats, FontConfig)
from pkgs.gui.button import Button
from pkgs.gui.multi_axis_graph import MultiAxisGraphWidget
from pkgs.gui.motor_ctrl_widget import MotorControlWidget


class Window(QMainWindow):
    """メインウィンドウクラス"""

    def __init__(self):
        super().__init__()

        self.init_ui()
        self.configure_ui()
        self.arrange_layouts()

    def init_ui(self):
        """UIの初期化
        """
        self.main_widget = QWidget()
        self.plot_area = MultiAxisGraphWidget()
        self.comport_ui = QWidget()
        self.motor_ui = MotorControlWidget()

        # レイアウト
        self.main_layout = QGridLayout()
        self.comport_ui_layout = QGridLayout()

        # ボタン
        self.save_button = Button('Save')
        self.plot_start_button = Button('Start', False)
        self.plot_stop_button = Button('Stop', False)
        self.plot_reset_button = Button('Reset', False)
        self.exit_button = Button('Exit')

        # テキストエリア
        self.line_edit = QLineEdit(
            dt.datetime.now().strftime(Formats.DATE_FMT))
        self.message_box = QLabel('シリアルポートを選択してください')

        # コンボボックス
        self.combobox1_label = QLabel('COM Port : ESP32 Dev Module')
        self.combobox1 = QComboBox()
        self.combobox2_label = QLabel('COM Port : RP2040 Xiao')
        self.combobox2 = QComboBox()

    def configure_ui(self):
        """UI要素の設定
        """
        self.setWindowTitle('KES-F System')
        self.setGeometry(100, 100, 800, 450)
        self.setCentralWidget(self.main_widget)
        self.plot_area.setMinimumSize(800, 450)
        self.comport_ui.setMaximumHeight(160)
        self.line_edit.setFont(
            QFont(FontConfig.FONT_FAMILY, FontConfig.FONT_SIZE))

        def get_serial_ports():
            ports = serial.tools.list_ports.comports()
            port_list = [port.device for port in ports]
            port_list.insert(0, '---')
            return port_list

        self.combobox1.addItems(get_serial_ports())
        self.combobox2.addItems(get_serial_ports())

    def arrange_layouts(self):
        """部品をレイアウトに追加
        """
        # main_layout
        self.main_widget.setLayout(self.main_layout)

        self.main_layout.addWidget(self.plot_area, 0, 1)
        self.main_layout.addWidget(self.comport_ui, 0, 0)
        self.main_layout.addWidget(self.save_button, 2, 0)
        self.main_layout.addWidget(self.plot_start_button, 3, 0)
        self.main_layout.addWidget(self.plot_stop_button, 4, 0)
        self.main_layout.addWidget(self.plot_reset_button, 5, 0)
        self.main_layout.addWidget(self.exit_button, 6, 0)
        self.main_layout.addWidget(self.line_edit, 2, 1)
        self.main_layout.addWidget(self.message_box, 6, 1)
        self.main_layout.addWidget(self.motor_ui, 3, 1, 4, 1)

        # comport_ui_layout
        self.comport_ui.setLayout(self.comport_ui_layout)

        self.comport_ui_layout.addWidget(self.combobox1_label, 0, 0)
        self.comport_ui_layout.addWidget(self.combobox1, 1, 0)
        self.comport_ui_layout.addWidget(self.combobox2_label, 2, 0)
        self.comport_ui_layout.addWidget(self.combobox2, 3, 0)
