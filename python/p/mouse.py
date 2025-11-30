from message import (MainCommandMessage, SubCommandMessage)
import pyautogui
from windows_toasts import Toast, WindowsToaster
from windows_toasts.wrappers import ToastDuration

def main(message: MainCommandMessage):
    '''
Show the current mouse position by x and y
'''
    print(pyautogui. position())
    toaster = WindowsToaster('Mouse Position')
    newToast = Toast([str(pyautogui.position())], duration=ToastDuration.Short)
    toaster.show_toast(newToast)
    input()
