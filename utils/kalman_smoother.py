# utils/kalman_smoother.py
from filterpy.kalman import KalmanFilter
import numpy as np

class KalmanSmoother:
    def __init__(self):
        self.kf = KalmanFilter(dim_x=4, dim_z=2)
        # 状态向量：[x, y, vx, vy]（位置+速度）
        self.kf.x = np.array([0, 0, 0, 0])
        # 状态转移矩阵（匀速模型）
        self.kf.F = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]])
        # 观测矩阵（只观测位置）
        self.kf.H = np.array([[1, 0, 0, 0], [0, 1, 0, 0]])
        # 噪声协方差（可根据抖动情况调整）
        self.kf.P *= 1000  # 初始不确定性
        self.kf.R = np.array([[0.02, 0], [0, 0.02]])  # 观测噪声
        self.kf.Q = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 10, 0], [0, 0, 0, 10]])  # 过程噪声

    def smooth(self, x, y):
        self.kf.predict()
        self.kf.update(np.array([x, y]))
        return self.kf.x[0], self.kf.x[1]