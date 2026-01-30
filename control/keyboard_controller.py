import pyautogui

class KeyboardController:
    def zoom_in(self):
        pyautogui.hotkey('ctrl', '+')
    
    def zoom_out(self):
        pyautogui.hotkey('ctrl', '-')