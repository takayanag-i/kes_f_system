import numpy as np
import pandas as pd

from pkgs.common.constants import ArithmeticConstants as const


class PlotArrayHandler:
    """プロットに使う配列のハンドリング
    """
    def __init__(self):
        """コンストラクタ"""
        self.reset_data()

    def reset_data(self):
        """データをリセット"""
        self.data_array = np.empty((0, 6))  # t, y1, y2, y3, y4, y5
        self.plot_array = np.empty((0, 6))  # t, y1, y2, y3, y4, y5

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
            tmp6 = float(tmp6) * const.MICRO
            return np.array([tmp6, tmp1, tmp2, tmp3, tmp4, tmp5])
        except ValueError:
            return None

    def update_arrays(self, data):
        """保存用配列に値を追加"""
        self.data_array = np.vstack((self.data_array, data))

    def update_plts(self, data):
        """表示用配列に値を追加"""
        self.plot_array = np.vstack((self.plot_array, data))
        return self.plot_array.T  # 転置して、個別の配列として返す

    def save_to_csv(self):
        """データをCSVに保存する"""
        columns = ['Time', 'F1', 'F2', 'Disp1', 'Disp2', 'Sensor']
        data = pd.DataFrame(self.data_array, columns=columns)
        data.to_csv(f"{self.window.line_edit.text()}.csv", index=False)
