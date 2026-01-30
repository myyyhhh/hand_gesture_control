# control/volume_controller.py
import pyautogui

class VolumeController:
    def increase_volume(self):
        # 每次按一下音量加
        pyautogui.press('volumeup')
        
    def decrease_volume(self):
        pyautogui.press('volumedown')
        
    def toggle_mute(self):
        pyautogui.press('volumemute')
        
