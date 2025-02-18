from message import (MainCommandMessage, SubCommandMessage)
import pyautogui
import time
import win32gui
import win32con


def main(message: MainCommandMessage):
    '''
Mouse clicking on screen repeatedly. Coordination, printed message and time interval can be changed in wait.main()
'''
    hwnd = win32gui.GetForegroundWindow()
    win32gui.SetWindowPos(hwnd,win32con.HWND_TOP,1,1,150,130,0)
    _mouse_move()

def no_resize(message: SubCommandMessage):
    '''
Mouse clicking on screen repeatedly. Coordination, printed message and time interval can be changed in wait.main()
Not resizing the cmd window
'''
    _mouse_move()

def _mouse_move():
    locs = [(200, 1050), (201,1050)]
    time_period = 100
    cur = 0
    while True:
        print('Err http://archive.ubuntu.com security release...')
        cur = (cur + 1) % 2
        pyautogui.moveTo(*locs[cur])
        pyautogui.click(*locs[cur])
        time.sleep(time_period)
        x, y = pyautogui.position()
        if (x, y) != locs[cur]:
            break 