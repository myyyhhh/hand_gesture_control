import math
import numpy as np

def calculate_distance(p1, p2):
    """计算两个归一化点之间的欧几里得距离"""
    return math.hypot(p2.x - p1.x, p2.y - p1.y)

def get_coords(landmark, width, height):
    """将归一化坐标转换为像素坐标"""
    return int(landmark.x * width), int(landmark.y * height)