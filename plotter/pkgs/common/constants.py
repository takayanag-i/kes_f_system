from enum import Enum, StrEnum


class Commands(bytes, Enum):
    """コマンド"""

    # プロッタ
    PLOT_START = b'0'
    PLOT_STOP = b'1'
    # モータ制御コマンド
    MOTOR_X_START = b'3'
    MOTOR_X_STOP = b'4'
    MOTOR_X_REVERSE = b'5'

    MOTOR_Y_START = b'7'
    MOTOR_Y_STOP = b'8'
    MOTOR_Y_REVERSE = b'9'


class ButtonLavels(StrEnum):
    ELONG_X_LAVEL = 'Xのばす'
    SHRINK_X_LAVEL = 'X縮める'
    REVERS_X_LAVEL = 'X逆回転'
    ELONG_Y_LAVEL = 'Yのばす'
    SHRINK_Y_LAVEL = 'Y縮める'
    REVERS_Y_LAVEL = 'Y逆回転'


class GraphLavels(StrEnum):
    """軸ラベル"""
    TIME_AX_LAVEL = 'Time / s</font>'
    FORCE_AX_LAVEL = 'Force / N</font>'
    DISP_AX_LAVEL = 'Displacement / mm</font>'
    SENSOR_AX_LAVEL = 'Sensor Output / V</font>'


class FontConfig:
    """フォント設定"""
    FONT_FAMILY = 'Arial'
    FONT_SIZE = 12


class ArithmeticConstants:
    """計算定数"""
    MICRO = 1e-6
    DATA_LENGTH = int(2**20)


class Formats(StrEnum):
    """フォーマット"""
    # テキスト
    DATE_FMT = '%Y-%m%d-%H%M-プロジェクト名'


class Styles(StrEnum):
    """スタイル"""
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
