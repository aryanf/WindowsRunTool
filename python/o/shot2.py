from message import (MainCommandMessage, SubCommandMessage)
import subprocess
import pyautogui

def main(message: MainCommandMessage):
    '''
Crop image of snipping tool, it is copied to clipboard
'''
    pyautogui.hotkey('win', 'shift', 's')

def edit(message:SubCommandMessage):
    '''
Open snipping tool, you can edit it later
'''
    subprocess.Popen(['snippingtool.exe'])
