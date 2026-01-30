# pipeline/action_mapper.py

from gesture.gesture_base import GestureType
from control.mouse_controller import MouseController
from control.volume_controller import VolumeController
from control.keyboard_controller import KeyboardController
from utils.smoothing import Smoother
from config import Settings
import pyautogui
import math
import time

class ActionMapper:
    def __init__(self):
        self.mouse = MouseController()
        self.volume = VolumeController()
        self.smoother = Smoother(Settings.SMOOTHING_FACTOR)
        
        # 状态追踪
        self.is_left_down = False
        self.is_right_down = False
        
        # 虚拟摇杆原点
        # 记录进入模式时的初始坐标 (x, y)
        self.origin_pos = None 
        # 防止静音重复触发的锁
        self.mute_triggered = False 
        
        self.prev_x = None
        self.prev_y = None
        self.remain_x = 0.0
        self.remain_y = 0.0

    def _apply_acceleration(self, dx, dy):
        magnitude = math.sqrt(dx**2 + dy**2)
        if magnitude < Settings.MOVE_THRESHOLD:
            return 0.0, 0.0
        if magnitude > Settings.ACCEL_THRESHOLD:
            gain = Settings.MOUSE_SENSITIVITY * (1 + (magnitude / Settings.ACCEL_THRESHOLD) * Settings.ACCEL_FACTOR)
        else:
            gain = Settings.MOUSE_SENSITIVITY
        max_gain = Settings.MOUSE_SENSITIVITY * 3
        gain = min(gain, max_gain)
        return dx * gain, dy * gain

    def execute(self, gesture, info):
        # 如果当前手势不是滚动或音量，重置原点，方便下次重新锁定
        if gesture not in [GestureType.SCROLL_MODE, GestureType.VOLUME_MODE]:
            self.origin_pos = None
            self.mute_triggered = False

        # ===========================
        # 1. 鼠标移动/点击逻辑
        # ===========================
        if gesture in [GestureType.POINTING, GestureType.DRAGGING] and info:
            curr_x, curr_y = self.smoother.get_smoothed_coords(info.x, info.y)
            if self.prev_x is None:
                self.prev_x, self.prev_y = curr_x, curr_y
            
            dx = (curr_x - self.prev_x) * 1.5
            dy = (curr_y - self.prev_y) * 1.5
            mx, my = self._apply_acceleration(dx, dy)
            
            self.remain_x += mx
            self.remain_y += my
            sx, sy = int(round(self.remain_x)), int(round(self.remain_y))
            self.remain_x -= sx
            self.remain_y -= sy
            
            if sx != 0 or sy != 0:
                self.mouse.move_relative(sx, sy)
            self.prev_x, self.prev_y = curr_x, curr_y
        else:
            self.prev_x = None
            self.smoother.reset()

        # 左键/右键状态管理
        should_left = (gesture == GestureType.DRAGGING or gesture == GestureType.LEFT_CLICK)
        if should_left and not self.is_left_down:
            self.mouse.drag_start()
            self.is_left_down = True
        elif not should_left and self.is_left_down:
            self.mouse.drag_end()
            self.is_left_down = False

        should_right = (gesture == GestureType.RIGHT_CLICK)
        if should_right and not self.is_right_down:
            pyautogui.mouseDown(button='right')
            self.is_right_down = True
        elif not should_right and self.is_right_down:
            pyautogui.mouseUp(button='right')
            self.is_right_down = False

        # ===========================
        # 2. 滚动模式逻辑
        # ===========================
        if gesture == GestureType.SCROLL_MODE and info:
            # 首次进入模式，记录原点
            if self.origin_pos is None:
                self.origin_pos = (info.x, info.y)
                return # 第一帧只记录，不操作

            # 计算当前手位置相对于原点的偏移
            diff_x = info.x - self.origin_pos[0]
            diff_y = info.y - self.origin_pos[1]

            # 死区判断 (Deadzone)，小幅度移动不触发
            if abs(diff_y) > Settings.JOYSTICK_DEADZONE:
                # 手向上(y变小) -> 偏移为负 -> 意图是页面向上滚动 -> scroll正值
                # 手向下(y变大) -> 偏移为正 -> 意图是页面向下滚动 -> scroll负值
                # 速度随距离增加
                speed_y = int(diff_y * Settings.SCROLL_SPEED)
                self.mouse.scroll_vertical(-speed_y) 

            if abs(diff_x) > Settings.JOYSTICK_DEADZONE:
                # 手向左(x变小) -> scroll 负/正取决于系统定义，通常左是负
                speed_x = int(diff_x * Settings.SCROLL_SPEED)
                self.mouse.scroll_horizontal(speed_x)

        # ===========================
        # 3. 音量控制逻辑
        # ===========================
        if gesture == GestureType.VOLUME_MODE and info:
            if self.origin_pos is None:
                self.origin_pos = (info.x, info.y)
                return

            diff_x = info.x - self.origin_pos[0]
            diff_y = info.y - self.origin_pos[1]

            # --- 音量增减 (垂直方向) ---
            if abs(diff_y) > Settings.VOLUME_TRIGGER_THRESHOLD:
                # 手向上(y变小, diff负) -> 音量增加
                # 手向下(y变大, diff正) -> 音量降低
                if diff_y < 0:
                    self.volume.increase_volume()
                else:
                    self.volume.decrease_volume()

            # --- 静音切换 (水平向左大距离) ---
            # 向左移动 (x 变小，diff_x 为负值) 且超过大阈值
            if diff_x < -Settings.MUTE_TRIGGER_THRESHOLD:
                if not self.mute_triggered:
                    self.volume.toggle_mute()
                    self.mute_triggered = True # 锁定，防止一直闪烁切换
            elif diff_x > -Settings.MUTE_TRIGGER_THRESHOLD * 0.5:
                # 只有手回到原点附近(迟滞比较)，才重置锁
                self.mute_triggered = False