# control/mouse_controller.py
import pyautogui
import numpy as np
import ctypes
from ctypes import wintypes
from config import Settings

# 禁用PyAutoGUI防故障
pyautogui.FAILSAFE = False

# 调用Windows User32.dll，发送鼠标滚动消息
user32 = ctypes.WinDLL('user32', use_last_error=True)

ULONG_PTR = ctypes.c_ulonglong

# 定义Windows API的结构体和常量
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR)  # 修复：替换为自定义的ULONG_PTR
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("mi", MOUSEINPUT)
    ]

# 鼠标消息常量：MOUSEEVENTF_WHEEL（垂直滚动）、MOUSEEVENTF_HWHEEL（水平滚动）
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_HWHEEL = 0x1000
INPUT_MOUSE = 0
# 滚动增量单位：Windows默认每滚轮格=120（和物理滚轮、触控板一致）
WHEEL_DELTA = 120

def send_mouse_wheel(dx=0, dy=0):
    """
    调用Windows原生API发送鼠标滚动消息（模拟触控板/物理滚轮）
    """
    inputs = INPUT * 2
    inp = inputs()
    count = 0

    # 处理垂直滚动
    if dy != 0:
        inp[count].type = INPUT_MOUSE
        inp[count].mi.dx = 0
        inp[count].mi.dy = 0
        inp[count].mi.mouseData = dy * WHEEL_DELTA  # 映射为Windows标准增量
        inp[count].mi.dwFlags = MOUSEEVENTF_WHEEL
        inp[count].mi.time = 0
        inp[count].mi.dwExtraInfo = 0  # 额外信息设为0即可
        count += 1

    # 处理水平滚动
    if dx != 0:
        inp[count].type = INPUT_MOUSE
        inp[count].mi.dx = 0
        inp[count].mi.dy = 0
        inp[count].mi.mouseData = dx * WHEEL_DELTA  # 映射为Windows标准增量
        inp[count].mi.dwFlags = MOUSEEVENTF_HWHEEL
        inp[count].mi.time = 0
        inp[count].mi.dwExtraInfo = 0  # 额外信息设为0
        count += 1

    # 发送滚动消息到系统 + 错误检查
    if count > 0:
        res = user32.SendInput(count, ctypes.byref(inp), ctypes.sizeof(INPUT))
        if res == 0:
            # 打印错误信息
            print(f"滚动消息发送失败，错误码：{ctypes.get_last_error()}")


class MouseController:
    def __init__(self):
        self.screen_w, self.screen_h = pyautogui.size()
        # 滚动灵敏度系数
        self.scroll_sensitivity = 0.1

    def move(self, x, y):
        """鼠标绝对移动"""
        screen_x = np.interp(x, [Settings.FRAME_MARGIN, Settings.CAP_WIDTH - Settings.FRAME_MARGIN], [0, self.screen_w])
        screen_y = np.interp(y, [Settings.FRAME_MARGIN, Settings.CAP_HEIGHT - Settings.FRAME_MARGIN], [0, self.screen_h])
        screen_x = np.clip(screen_x, 0, self.screen_w)
        screen_y = np.clip(screen_y, 0, self.screen_h)
        pyautogui.moveTo(screen_x, screen_y)

    def move_relative(self, dx, dy):
        """鼠标相对移动"""
        pyautogui.moveRel(int(dx), int(dy), _pause=False)

    def left_click(self):
        pyautogui.click()

    def right_click(self):
        pyautogui.rightClick()
    
    def drag_start(self):
        pyautogui.mouseDown()
        
    def drag_end(self):
        pyautogui.mouseUp()

    # 触控板式垂直滚动
    def scroll_vertical(self, distance):
        if abs(distance) < 0.01:
            return
        scroll_delta = int(distance * Settings.SCROLL_SPEED * self.scroll_sensitivity)
        send_mouse_wheel(dy=scroll_delta)

    # 触控板式水平滚动
    def scroll_horizontal(self, distance):
        if abs(distance) < 0.01:
            return
        scroll_delta = int(distance * Settings.SCROLL_SPEED * self.scroll_sensitivity)
        send_mouse_wheel(dx=scroll_delta)