# utils/smoothing.py

class Smoother:
    def __init__(self, smoothing_factor=0.2):
        # 初始化时保留老版本的默认值（0.2），同时保存为实例属性
        self.smoothing_factor = smoothing_factor  # 核心：保留实例属性，保证帧间计算稳定
        self.smoothed_x = None
        self.smoothed_y = None
        self.is_first = True  

    def get_smoothed_coords(self, x, y):
        """
        x,y：传入的原始坐标

        Return：平滑后的坐标
        """
        x, y = float(x), float(y)
        # 首次帧/重置后，直接赋值，无平滑
        if self.is_first or self.smoothed_x is None or self.smoothed_y is None:
            self.smoothed_x = x
            self.smoothed_y = y
            self.is_first = False
        else:
            self.smoothed_x = self.smoothing_factor * x + (1 - self.smoothing_factor) * self.smoothed_x
            self.smoothed_y = self.smoothing_factor * y + (1 - self.smoothing_factor) * self.smoothed_y
        return self.smoothed_x, self.smoothed_y

    def reset(self):
        """重置平滑器状态"""
        self.smoothed_x = None
        self.smoothed_y = None
        self.is_first = True

    def update_smoothing_factor(self, new_factor):
        """
        GUI实时调节的参数更新接口
        """
        # 做范围限制，防止传入无效值（0.0~1.0）
        self.smoothing_factor = max(0.0, min(1.0, float(new_factor)))