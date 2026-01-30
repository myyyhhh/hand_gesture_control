# configs.py

import cv2

class Settings:
    # 摄像头设置
    CAMERA_ID = 0
    CAP_WIDTH = 640
    CAP_HEIGHT = 480
    FPS = 30

    # 手部检测配置
    MAX_NUM_HANDS = 1
    MIN_DETECTION_CONFIDENCE = 0.7
    MIN_TRACKING_CONFIDENCE = 0.5

    # 屏幕映射范围 (避免手必须伸到摄像头边缘才能碰到屏幕边缘)
    FRAME_MARGIN = 100  # 像素

    # 动作阈值 (归一化坐标 0-1)
    CLICK_THRESHOLD = 0.04       # 食指与大拇指距离阈值
    R_CLICK_THRESHOLD = 0.04     # 中指与大拇指距离阈值
    SCROLL_THRESHOLD = 0.05      # 滚轮触发阈值
    
    # 鼠标灵敏度
    MOUSE_SENSITIVITY = 800

    # 平滑系数 (0.0 - 1.0, 越小越平滑但延迟越高)
    SMOOTHING_FACTOR = 0.2
    
    # 功能开关
    ENABLE_MOUSE = True
    ENABLE_VOLUME = True
    ENABLE_SCROLL = True
    ENABLE_ZOOM = True

    
    # 鼠标加速算法阈值
    MOVE_THRESHOLD = 0.001    # 死区
    ACCEL_THRESHOLD = 0.005   # 加速阈值
    ACCEL_FACTOR = 1.5        # 加速倍率



    # 虚拟摇杆死区（在这个范围内不触发滚动/音量变化）
    JOYSTICK_DEADZONE = 0.05 
    
    # 滚动速度系数
    SCROLL_SPEED = 10
    
    # 音量触发阈值（距离原点的偏移量）
    VOLUME_TRIGGER_THRESHOLD = 0.05
    
    # 静音触发阈值（向左移动的大距离）
    MUTE_TRIGGER_THRESHOLD = 0.15


    # GUI配置
    GUI_WIDTH = 950  # GUI窗口宽度
    GUI_HEIGHT = 650 # GUI窗口高度
    VIDEO_DISPLAY_SIZE = (640, 480) # 摄像头画面显示尺寸
    # 可调节参数范围（供GUI滑块使用）
    PARAM_RANGES = {
        "mouse_sensitivity": (200, 1500, 10),    # 800默认值，范围200-1500
        "smoothing_factor": (0.0, 1.0, 0.01),
        "scroll_speed": (5, 50, 1),              # 20默认值
        "accel_factor": (0.5, 3.0, 0.1),         # 1.5默认值
        "joystick_deadzone": (0.01, 0.2, 0.01)   # 0.05默认值
    }