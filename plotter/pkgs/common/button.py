from PyQt6.QtWidgets import QPushButton


class Button(QPushButton):
    """ボタンを生成するクラス

    @Override QPushButton
    """

    def __init__(self, text, callback, is_enable=True):
        """コンストラクタ

        Arguments:
            text -- ボタンテキスト
            callback -- コールバック関数
            is_enable -- 押下可否 (default: True)
        """
        super().__init__(text)
        self.clicked.connect(callback)
        self.setEnabled(is_enable)
