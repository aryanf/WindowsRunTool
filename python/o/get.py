from time import sleep
from message import (MainCommandMessage, SubCommandMessage)
import subprocess
import pyautogui
import win32gui
import win32con

def main(message: MainCommandMessage):
    '''
This need PowerToy to run in background
Get text from screen (run PowerToy Text Extractor)
'''
    hwnd = win32gui.GetForegroundWindow()
    win32gui.SetWindowPos(hwnd,win32con.HWND_BOTTOM,1,1,500,300,0)
    pyautogui.hotkey('win', 'shift', 't')

def text(message:SubCommandMessage):
    '''
This need PowerToy to run in background
Get text from screen (run PowerToy Text Extractor)
'''
    hwnd = win32gui.GetForegroundWindow()
    win32gui.SetWindowPos(hwnd,win32con.HWND_BOTTOM,1,1,500,300,0)
    pyautogui.hotkey('win', 'shift', 't')
