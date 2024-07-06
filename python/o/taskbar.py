from message import (MainCommandMessage, SubCommandMessage)
import os


def main(message: MainCommandMessage):
    '''
Restart the taskbar by killing explorer process and creating a new one
'''
    os.system('taskkill /f /im explorer.exe')
    os.system('start explorer.exe')