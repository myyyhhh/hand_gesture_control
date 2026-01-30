# hand_gesture_control/main.py

import cv2
import time
from config import Settings
from vision.camera import Camera
from vision.hand_detector import HandDetector
from gesture.gesture_recognizer import GestureRecognizer
from pipeline.action_mapper import ActionMapper
from utils.fps_counter import FpsCounter
from utils.logger import log

def main():
    # 初始化模块
    camera = Camera()           # 相机
    detector = HandDetector()         # 手部检测器
    recognizer = GestureRecognizer()  # 手势识别器
    mapper = ActionMapper()           # 动作映射器
    fps_counter = FpsCounter()        # FPS 计数器

    log("Hand Gesture Control System Started.")
    log("Press 'q' to exit.")

    while True:
        # 1. 读取画面 
        success, img = camera.read() # 
        if not success:
            break

        # 2. 检测手部
        img = detector.find_hands(img) # 绘制手部关键点+骨骼连线，返回带绘制的画面
        lm_list = detector.get_landmarks() # 获取检测到的手部关键点列表

        if lm_list:
            landmarks = lm_list.landmark # 提取关键点的归一化坐标列表
            
            # 3. 更新手指状态
            recognizer.update_fingers_status(landmarks, Settings.CAP_HEIGHT)
            
            # 4. 识别手势
            gesture_type, info = recognizer.recognize(landmarks)
            
            # 5. 执行动作
            mapper.execute(gesture_type, info)
            
            # UI 显示
            cv2.putText(img, f"Gesture: {gesture_type.name}", (10, 50), 
                        cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

        # FPS 显示
        fps = fps_counter.update()
        cv2.putText(img, f"FPS: {fps}", (10, 20), 
                    cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 1)

        # 显示画面
        cv2.imshow("Hand Control", img)
        
        # 退出
        if cv2.waitKey(1) & 0xFF == 27:
            break

    camera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()