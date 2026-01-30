# gesture/gesture_base.py
from enum import Enum, auto

class GestureType(Enum):
    NONE = auto()
    POINTING = auto()      # 移动鼠标
    LEFT_CLICK = auto()    # 左键点击
    RIGHT_CLICK = auto()   # 右键点击
    DRAGGING = auto()      # 拖拽

    SCROLL_MODE = auto()   # 滚轮模式
    VOLUME_MODE = auto()   # 音量模式

    ZOOM_IN = 7
    ZOOM_OUT = 8