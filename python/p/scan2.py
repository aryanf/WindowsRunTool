from time import sleep
from message import (MainCommandMessage, SubCommandMessage)
import pyautogui
import win32gui
import win32con
import psutil

def _is_powertoys_running():
    for process in psutil.process_iter(['name']):
        if 'PowerToys' in process.info['name']:
            return True
    return False

def main(message: MainCommandMessage):
    '''
This need PowerToys to run in background
Get text from screen (run PowerToy Text Extractor)
'''
    if not _is_powertoys_running():
        input("PowerToys needs to run in the background. Run PowerToys ...")
        return
    hwnd = win32gui.GetForegroundWindow()
    win32gui.SetWindowPos(hwnd,win32con.HWND_BOTTOM,1,1,500,300,0)
    pyautogui.hotkey('win', 'shift', 't')