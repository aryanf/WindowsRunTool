from message import (MainCommandMessage, SubCommandMessage)
from win10toast import ToastNotifier
import pyautogui

def main(message: MainCommandMessage):
    '''
Show the current mouse position by x and y
'''
    print(pyautogui. position())
    toaster = ToastNotifier()
    toaster.show_toast("Mouse", str(pyautogui.position()), duration=5)
    input()
