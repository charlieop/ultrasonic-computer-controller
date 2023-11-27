import pyautogui

def noAction(param = None):
    pass

PRESS = lambda key: pyautogui.press(key)
KEY_DOWN = lambda key: pyautogui.keyDown(key)
KEY_UP = lambda key: pyautogui.keyUp(key)
SCROLL = lambda amount: pyautogui.vscroll(amount)
NO_ACTION = lambda: None
CLICK = lambda: pyautogui.click()

class Presets:
    YOUTUBE = {
        "up": ((PRESS, "up"),),
        "down": ((PRESS, "down"),),
        "left": ((PRESS, "left"),),
        "right": ((PRESS, "right"),),
        "single tap": ((NO_ACTION, None),),
        "double tap": ((PRESS, "playpause"),),
        "triple tap": ((PRESS, "esc"),),
    }

    WEB = {
        "up": ((SCROLL, 5),),
        "down": ((SCROLL, -5),),
        "left": ((KEY_DOWN, "shift"), (PRESS, "tab"), (KEY_UP, "shift"),),
        "right": ((PRESS, "tab"),),
        "single tap": ((PRESS, "space"),),
        "double tap": ((PRESS, "enter"),),
        "triple tap": ((PRESS, "esc"),),
    }


class ConputerController:
    def __init__(self, presets):
        self.presets = presets
    def changePreset(self, presets):
        self.presets = presets
    def makeAction(self, gesture):
        action = self.presets[gesture]
        if action is None:
            return
        for item in action:
            func, param = item  # Unpack the tuple into function and parameter
            if param is None:
                func()
            func(param)  # Call the function with the parameter
            