from message import (MainCommandMessage, SubCommandMessage, get_open_source_app_dir)
import pyautogui
import win32gui
import win32con
import psutil
import os
import subprocess
import time

app_path = os.path.join(get_open_source_app_dir(), 'ZoomIt', 'ZoomIt.exe')

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
        print('ZoomIt is not running. Running ZoomIt first.')
        subprocess.Popen([app_path])
        time.sleep(2)
    print('use Ctrl+1 to zoom in, Ctrl+2 to draw.')
    hwnd = win32gui.GetForegroundWindow()
    win32gui.SetWindowPos(hwnd,win32con.HWND_BOTTOM,1,1,500,300,0)
    pyautogui.hotkey('ctrl', '2')