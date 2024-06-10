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
            tmp6 = float(tmp6) * const.MICRO
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
        return self.t_plt, self.y1_plt, self.y2_plt, self.y3_plt, \
            self.y4_plt, self.y5_plt

    def save_to_csv(self):
        """データをCSVに保存する"""
        array = np.array([self.t, self.y1, self.y2, self.y3, self.y4, self.y5])
        array = array.T
        columns = ['Time', 'F1', 'F2', 'Disp1', 'Disp2', 'Sensor']
        data = pd.DataFrame(array, columns=columns)
        data.to_csv(f"{self.window.line_edit.text()}.csv", index=False)
