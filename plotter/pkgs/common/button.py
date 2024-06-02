from PyQt6.QtWidgets import QPushButton


class Button(QPushButton):
    """ボタンを生成するクラス

    @Override QPushButton
    """

    def __init__(self, text, is_enable=True):
        """コンストラクタ

        Arguments:
            text -- ボタンテキスト
            is_enable -- 押下可否 (default: True)
        """
        super().__init__(text)
        self.setEnabled(is_enable)

    def set_callback(self, callback):
        """コールバック関数をセットする

        Arguments:
            callback -- ボタン押下時に発火する関数
        """

        self.clicked.connect(callback)
