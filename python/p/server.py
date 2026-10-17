from message import (MainCommandMessage, SubCommandMessage)
import time
import win32gui
import time

def get_teams_windows():
    windows = []

    def enum_handler(hwnd, lParam):
        title = win32gui.GetWindowText(hwnd)
        if "Teams" in title:
            windows.append(title)
    win32gui.EnumWindows(enum_handler, None)
    return windows

def is_teams_in_call():
    for title in get_teams_windows():
        if "call" in title.lower() or "meeting" in title.lower():
            return True
    return False

def main(message: MainCommandMessage):
    in_call = False
    print('on main function')
    # _loop()
    
def _loop():
    while True:
        if is_teams_in_call():
            if not in_call:
                print("Teams is in a call!")
                in_call = True
        else:
            if in_call:
                print("No call detected.")
                in_call = False
        time.sleep(60)  # check every minute