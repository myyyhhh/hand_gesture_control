# gui_main.py

import mediapipe as mp
import cv2

import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import GestureControlWindow

if __name__ == "__main__":

    QApplication.setStyle("Fusion")
    app = QApplication(sys.argv)
    window = GestureControlWindow()
    window.show()
    sys.exit(app.exec_())