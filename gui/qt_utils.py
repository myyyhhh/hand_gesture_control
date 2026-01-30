# gui/qt_utils.py
import cv2
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import numpy as np

class CV2QtConverter:
    """OpenCV画面转PyQt5可用格式"""
    @staticmethod
    def cv2pixmap(cv_img, size=None):
        """
        cv_img: OpenCV读取的BGR图像
        size: (w, h) 目标显示尺寸
        return: QPixmap
        """
        if cv_img is None or cv_img.size == 0:
            return QPixmap()
        # BGR转RGB
        rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_img.shape
        bytes_per_line = ch * w
        # 转换为QImage
        q_img = QImage(rgb_img.data, w, h, bytes_per_line, QImage.Format_RGB888)
        # 缩放尺寸
        if size:
            q_img = q_img.scaled(size[0], size[1], aspectRatioMode=1)
        return QPixmap.fromImage(q_img)

class WorkerThread(QThread):
    """手势识别线程"""
    frame_signal = pyqtSignal(np.ndarray)  # 画面信号
    status_signal = pyqtSignal(dict)       # 状态信号（FPS、手势、参数）
    error_signal = pyqtSignal(str)         # 错误信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = False  # 线程运行标志
        self.params = {}      # 从GUI传入的实时参数

    def set_params(self, params):
        """更新从GUI调节的参数"""
        self.params.update(params)

    def run(self):
        try:
            from config import Settings
            from vision.camera import Camera
            from vision.hand_detector import HandDetector
            from gesture.gesture_recognizer import GestureRecognizer
            from pipeline.action_mapper import ActionMapper
            from utils.fps_counter import FpsCounter
            from utils.logger import log

            # 初始化核心模块
            camera = Camera()
            detector = HandDetector()
            recognizer = GestureRecognizer()
            mapper = ActionMapper()
            fps_counter = FpsCounter()
            self.running = True
            log("GUI版手势控制系统启动")

            while self.running:
                # 读取画面
                success, img = camera.read()
                if not success:
                    self.error_signal.emit("摄像头读取失败")
                    break

                # 动态更新配置（从GUI传入）
                for k, v in self.params.items():
                    if hasattr(Settings, k.upper()):
                        setattr(Settings, k.upper(), v)
                    # 同步更新动作映射器的平滑系数
                    if k == "smoothing_factor" and hasattr(mapper, "smoother"):
                        mapper.smoother.smoothing_factor = v
                    if k == "accel_factor" and hasattr(Settings, "ACCEL_FACTOR"):
                        Settings.ACCEL_FACTOR = v

                # 手部检测与手势识别
                img = detector.find_hands(img)
                lm_list = detector.get_landmarks()
                gesture_type = None
                if lm_list:
                    landmarks = lm_list.landmark
                    recognizer.update_fingers_status(landmarks, Settings.CAP_HEIGHT)
                    gesture_type, info = recognizer.recognize(landmarks)
                    mapper.execute(gesture_type, info)
                    # 绘制手势信息
                    cv2.putText(img, f"Gesture: {gesture_type.name}", (10, 50),
                                cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

                # 计算FPS并绘制
                fps = fps_counter.update()
                cv2.putText(img, f"FPS: {fps}", (10, 20),
                            cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 1)

                # 发送信号到UI
                self.frame_signal.emit(img)
                self.status_signal.emit({
                    "fps": fps,
                    "gesture": gesture_type.name if gesture_type else "NONE",
                    "camera": f"{Settings.CAP_WIDTH}x{Settings.CAP_HEIGHT}"
                })

            # 释放资源
            camera.release()
            log("GUI版手势控制系统停止")
        except Exception as e:
            self.error_signal.emit(f"程序运行错误: {str(e)}")
            self.running = False

    def stop(self):
        """停止线程"""
        self.running = False
        self.wait()