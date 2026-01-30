import cv2
from config import Settings

class Camera:
    def __init__(self):
        self.cap = cv2.VideoCapture(Settings.CAMERA_ID)
        self.cap.set(3, Settings.CAP_WIDTH)
        self.cap.set(4, Settings.CAP_HEIGHT)

    def read(self):
        success, img = self.cap.read()
        if success:
            # 翻转图像，使其像照镜子一样自然
            return True, cv2.flip(img, 1)
        return False, None

    def release(self):
        self.cap.release()