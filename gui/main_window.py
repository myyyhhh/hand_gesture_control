# gui/main_window.py
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QSlider, QGroupBox, QTextEdit,
                             QGridLayout, QStatusBar, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont
from config import Settings
from .qt_utils import CV2QtConverter, WorkerThread
import numpy as np


class GestureControlWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("手势控制系统 - GUI版")
        self.setFixedSize(Settings.GUI_WIDTH, Settings.GUI_HEIGHT)
        self.worker = None  # 手势识别线程
        self.init_ui()
        self.init_status_bar()

    def init_ui(self):
        """初始化UI布局"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 左侧：实时画面+启停按钮
        left_layout = QVBoxLayout()
        self.video_label = QLabel()
        self.video_label.setFixedSize(*Settings.VIDEO_DISPLAY_SIZE)
        self.video_label.setStyleSheet("border: 2px solid #333;")
        self.video_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.video_label)

        # 启停按钮
        self.start_btn = QPushButton("启动系统")
        self.stop_btn = QPushButton("停止系统")
        self.start_btn.setFixedHeight(40)
        self.stop_btn.setFixedHeight(40)
        self.stop_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.start_system)
        self.stop_btn.clicked.connect(self.stop_system)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        left_layout.addLayout(btn_layout)
        main_layout.addLayout(left_layout)

        # 右侧：参数调节+状态监控+操作说明
        right_layout = QVBoxLayout()
        right_layout.setSpacing(15)

        # 1. 参数调节面板
        param_group = QGroupBox("参数调节（实时生效）")
        param_layout = QGridLayout(param_group)
        self.param_sliders = {}
        # 遍历配置的可调节参数，生成滑块
        param_labels = {
            "mouse_sensitivity": "鼠标灵敏度",
            "smoothing_factor": "鼠标平滑系数",
            "scroll_speed": "滚动速度",
            "volume_sensitivity": "音量调节步长",
            "accel_factor": "鼠标加速系数",
            "joystick_deadzone": "摇杆触发死区"
        }
        row = 0
        for param, (min_val, max_val, step) in Settings.PARAM_RANGES.items():
            # 标签
            label = QLabel(param_labels[param])
            label.setFont(QFont("SimHei", 9))
            # 数值显示
            self.param_sliders[param] = {"slider": QSlider(Qt.Horizontal), "label": QLabel(f"{getattr(Settings, param.upper(), min_val)}")}
            slider = self.param_sliders[param]["slider"]
            # 设置滑块范围（浮点型转整型，步长适配）
            if isinstance(min_val, float):
                slider.setRange(int(min_val*100), int(max_val*100))
                slider.setValue(int(getattr(Settings, param.upper(), min_val)*100))
                slider.setSingleStep(int(step*100))
            else:
                slider.setRange(min_val, max_val)
                slider.setValue(getattr(Settings, param.upper(), min_val))
                slider.setSingleStep(step)
            slider.valueChanged.connect(lambda v, p=param: self.update_param(p, v))
            # 布局
            param_layout.addWidget(label, row, 0)
            param_layout.addWidget(slider, row, 1)
            param_layout.addWidget(self.param_sliders[param]["label"], row, 2)
            row += 1
        right_layout.addWidget(param_group)

        # 2. 状态监控面板
        status_group = QGroupBox("系统状态")
        status_layout = QGridLayout(status_group)
        self.status_labels = {
            "fps": QLabel("0"),
            "gesture": QLabel("NONE"),
            "camera": QLabel(f"{Settings.CAP_WIDTH}x{Settings.CAP_HEIGHT}")
        }
        status_items = [("当前FPS", "fps"), ("识别手势", "gesture"), ("摄像头分辨率", "camera")]
        for row, (name, key) in enumerate(status_items):
            status_layout.addWidget(QLabel(name), row, 0)
            status_layout.addWidget(self.status_labels[key], row, 1)
        right_layout.addWidget(status_group)

        # 3. 操作说明面板
        help_group = QGroupBox("手势操作说明")
        help_layout = QVBoxLayout(help_group)
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setFont(QFont("SimHei", 8))
        help_text.setText("""
【鼠标控制】
- 小指伸直：鼠标移动（食指根部为光标）
- 食指+小指伸直：鼠标拖拽
- 食指单独伸直：左键点击/拖拽
- 中指单独伸直：右键点击

【滚动控制】
- 仅拇指伸直：进入滚动模式（上下/左右移动手掌控制滚动）

【音量控制】
- 五指全开：进入音量模式
  - 手掌上下移动：调节音量
  - 手掌大幅左移：静音/取消静音

【退出/暂停】
- 点击GUI「停止系统」按钮即可暂停
        """)
        help_layout.addWidget(help_text)
        right_layout.addWidget(help_group)

        main_layout.addLayout(right_layout)

    def init_status_bar(self):
        """初始化状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("系统未启动，点击「启动系统」开始使用", 0)

    def update_param(self, param, value):
        """更新参数值并同步到线程"""
        min_val, max_val, step = Settings.PARAM_RANGES[param]
        # 还原浮点型数值
        if isinstance(min_val, float):
            real_val = round(value / 100, 2)
        else:
            real_val = value
        # 更新显示
        self.param_sliders[param]["label"].setText(f"{real_val}")
        # 同步到工作线程
        if self.worker and self.worker.isRunning():
            self.worker.set_params({param: real_val})

    def start_system(self):
        """启动手势识别系统"""
        if self.worker and self.worker.isRunning():
            QMessageBox.information(self, "提示", "系统已在运行中！")
            return
        # 初始化工作线程
        self.worker = WorkerThread()
        self.worker.frame_signal.connect(self.update_video)
        self.worker.status_signal.connect(self.update_status)
        self.worker.error_signal.connect(self.show_error)
        # 传递初始参数
        init_params = {}
        for param in Settings.PARAM_RANGES:
            min_val = Settings.PARAM_RANGES[param][0]
            if isinstance(min_val, float):
                init_params[param] = round(int(self.param_sliders[param]["slider"].value())/100, 2)
            else:
                init_params[param] = self.param_sliders[param]["slider"].value()
        self.worker.set_params(init_params)
        # 启动线程
        self.worker.start()
        # 更新UI状态
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_bar.showMessage("系统运行中，请勿遮挡摄像头", 0)

    def stop_system(self):
        """停止手势识别系统"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker = None
            # 清空画面
            self.video_label.clear()
            self.video_label.setText("摄像头画面已停止")
            # 更新UI状态
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.status_bar.showMessage("系统已停止，点击「启动系统」重新开始", 0)
            # 重置状态显示
            for label in self.status_labels.values():
                if label.text() != f"{Settings.CAP_WIDTH}x{Settings.CAP_HEIGHT}":
                    label.setText("0" if label.text().isdigit() else "NONE")

    @pyqtSlot(np.ndarray)
    def update_video(self, cv_img):
        """更新实时画面"""
        pixmap = CV2QtConverter.cv2pixmap(cv_img, Settings.VIDEO_DISPLAY_SIZE)
        self.video_label.setPixmap(pixmap)

    @pyqtSlot(dict)
    def update_status(self, status):
        """更新系统状态"""
        for k, v in status.items():
            if k in self.status_labels:
                self.status_labels[k].setText(str(v))

    @pyqtSlot(str)
    def show_error(self, error_msg):
        """显示错误信息"""
        QMessageBox.critical(self, "错误", error_msg)
        self.stop_system()

    def closeEvent(self, event):
        """窗口关闭事件，确保线程正常退出"""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(self, "确认", "系统正在运行中，是否确定关闭？",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.stop_system()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()