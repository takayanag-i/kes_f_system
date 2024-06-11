from enum import Enum, StrEnum


class Commands(bytes, Enum):
    """コマンド"""
    # プロッタ
    PLOT_START = b'0'
    PLOT_STOP = b'1'
    # モータ制御コマンド
    MOTOR_START1 = b'3'
    MOTOR_STOP1 = b'4'
    MOTOR_REVERSE1 = b'5'
    MOTOR_START2 = b'7'
    MOTOR_STOP2 = b'8'
    MOTOR_REVERSE2 = b'9'


class ButtonLabels(StrEnum):
    """ボタンのラベル"""
    ELONG1 = '1のばす'
    SHRINK1 = '1縮める'
    REVERSE1 = '1逆回転'
    ELONG2 = '2のばす'
    SHRINK2 = '2縮める'
    REVERSE2 = '2逆回転'


class GraphLabels(StrEnum):
    """軸ラベル"""
    TIME_AX = 'Time / s'
    FORCE_AX = 'Force / N'
    DISP_AX = 'Displacement / mm'
    SENSOR_AX = 'Sensor Output / V'


class FontConfig:
    """フォント設定"""
    FONT_FAMILY = 'Arial'
    FONT_SIZE = 12


class ArithmeticConstants:
    """計算定数"""
    MICRO = 1e-6
    DATA_LENGTH = int(2**20)


class RangeValues:
    """範囲の設定"""
    X_RANGE = (0, 50)
    Y_RANGE1 = (-0.1, 3.3)
    Y_RANGE2 = (-10, 10)
    RIGHT_AXIS_RANGE = (-10, 10)


class ColourValues:
    """色の設定"""
    LIGHT_BLUE = '#DDEEFF'
    BLUE = '#99DDFF'
    GREEN = '#B5FF14'
    RED = '#FF0000'
    YELLOW = '#FFFF00'
    WHITE = '#FFFFFF'


class Formats(StrEnum):
    """フォーマット"""
    # テキスト
    DATE_FMT = '%Y-%m%d-%H%M-プロジェクト名'


class DataProperties:
    """レコードの属性"""
    PROPERTIES = {
        1: 'Time',
        2: 'Force1',
        3: 'Force',
        4: 'Disp1',
        5: 'Disp2',
        6: 'Sensor'
    }

    @classmethod
    def get_property(cls, key):
        """キーに対応するプロパティを取得"""
        return cls.PROPERTIES.get(key)

    @classmethod
    def list_properties(cls):
        """プロパティのリストを取得"""
        return list(cls.PROPERTIES.values())

    @classmethod
    def list_keys(cls):
        """キーのリストを取得"""
        return list(cls.PROPERTIES.keys())

    @classmethod
    def get_key(cls, property_name):
        """プロパティ名に対応するキーを取得"""
        for key, value in cls.PROPERTIES.items():
            if value == property_name:
                return key
        return None


class Styles:
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
    LABEL_STYLE = {'color': ColourValues.WHITE, 'font-size': '12pt'}
