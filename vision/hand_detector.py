import mediapipe as mp
print(mp.__file__)
import cv2
from config import Settings

class HandDetector:
    """
    手部检测器类，使用MediaPipe进行手部关键点检测和跟踪
    """
    def __init__(self):
        """
        初始化手部检测器
        """
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=Settings.MAX_NUM_HANDS,
            min_detection_confidence=Settings.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=Settings.MIN_TRACKING_CONFIDENCE
        )
        self.mp_draw = mp.solutions.drawing_utils

    def find_hands(self, img, draw=True):
        """
        在图像中检测手部并绘制关键点
        
        Args:
            img: 输入图像
            draw: 是否在图像上绘制手部关键点连接线，默认为True
            
        Returns:
            处理后的图像
        """
        # 将BGR图像转换为RGB格式,以适应MediaPipe处理要求
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # 运行MediaPipe手部检测模型
        self.results = self.hands.process(img_rgb)
        
        # 如果检测到手部关键点且需要绘制，则在图像上绘制连接线
        if self.results.multi_hand_landmarks and draw:
            for hand_lms in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
        
        return img

    def get_landmarks(self):
        """
        获取检测到的第一只手的关键点数据
        
        Returns:
            第一只手的关键点数据，如果未检测到则返回None
        """
        if self.results.multi_hand_landmarks:
            return self.results.multi_hand_landmarks[0] # 只返回第一只手
        return None
