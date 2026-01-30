# gesture/gesture_recognizer.py

import math
from typing import List, Tuple, Optional
# from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmarkList
from .gesture_base import GestureType

class GestureRecognizer:
    def __init__(self) -> None:
        # 存储5根手指状态：0-拇指, 1-食指, 2-中指, 3-无名指, 4-小指0
        self.fingers: List[int] = [] 

    def update_fingers_status(self, lm, height: int) -> List[int]:
        """更新五根手指的状态 (1:伸直, 0:弯曲)"""
        # 指尖ID: 拇指4, 食指8, 中指12, 无名指16, 小指20
        # 关节ID: 拇指IP 3, 其他手指PIP [6, 10, 14, 18]
        tip_ids = [4, 8, 12, 16, 20]
        finger_status: List[int] = []

        # 1. 判断大拇指 (Thumb)
        # 逻辑：对于掌心朝向镜头，如果拇指指尖(4)的x坐标 在 小指指根(17) 的外侧（距离更远），视为伸展
        if abs(lm[4].x - lm[9].x) > abs(lm[3].x - lm[9].x):
            finger_status.append(1) # 拇指伸直
        else:
            finger_status.append(0) # 拇指弯曲

        # 2. 判断其余四指 (Index, Middle, Ring, Pinky)
        # 逻辑：指尖y < 关节y (屏幕坐标系向下为正，指尖在上数值小)
        pip_ids = [6, 10, 14, 18]
        for i in range(1, 5): # 对应 tip_ids[1] 到 tip_ids[4]
            if lm[tip_ids[i]].y < lm[pip_ids[i-1]].y:
                finger_status.append(1)
            else:
                finger_status.append(0)

        self.fingers = finger_status
        return finger_status

    def recognize(self, lm) -> Tuple[GestureType, Optional[object]]:
        if not lm:
            return GestureType.NONE, None

        # 解包手指状态 [拇指, 食指, 中指, 无名指, 小指]
        thumb, index, middle, ring, pinky = self.fingers
        
        # 获取手掌中心用于定位 (中指根9)
        hand_center = lm[9] 

        # 1. 滚动状态: 大拇指展开(1) 且 四指弯曲(0)：[1, 0, 0, 0, 0]
        if thumb == 1 and index == 0 and middle == 0 and ring == 0 and pinky == 0:
            return GestureType.SCROLL_MODE, hand_center

        # 2. 音量控制状态: 大拇指展开(1) 且 四指展开(1) -> 五指全开
        if all(f == 1 for f in self.fingers):
            return GestureType.VOLUME_MODE, hand_center

        # 3. 鼠标控制
        
        # 鼠标移动：小指伸直，且不是全开(音量模式)
        if pinky == 1 and not (index == 1 and middle == 1 and thumb == 1):
            cursor_point = lm[5] # 食指根部作为光标源
            if index == 1:
                return GestureType.DRAGGING, cursor_point
            return GestureType.POINTING, cursor_point

        # 左键/右键 (原地操作，小指弯曲)
        if pinky == 0:
            if index == 1 and middle == 0 and ring == 0:
                return GestureType.LEFT_CLICK, None
            if index == 0 and middle == 1 and ring == 0:
                return GestureType.RIGHT_CLICK, None

        # 默认状态：不做操
        return GestureType.NONE, None