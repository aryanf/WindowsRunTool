from message import (MainCommandMessage, SubCommandMessage)
import pyautogui
import win32gui
import win32con
import psutil

def _is_zoomit_running():
    for process in psutil.process_iter(['name']):
        if 'ZoomIt' in process.info['name']:
            return True
    return False

def main(message: MainCommandMessage):
    '''
This need ZoomIt to run in background
Draw on screen (run ZoomIt)
Right click or Esc to exit
'''
    if not _is_zoomit_running():
        input("PowerToys is running in the background. Run PowerToys ...")
        return
    hwnd = win32gui.GetForegroundWindow()
    win32gui.SetWindowPos(hwnd,win32con.HWND_BOTTOM,1,1,500,300,0)
    pyautogui.hotkey('ctrl', '2')