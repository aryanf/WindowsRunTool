from message import (MainCommandMessage, SubCommandMessage)
import pyautogui

def main(message: MainCommandMessage):
    '''
Show the current mouse position by x and y
'''
    print(pyautogui. position())
    input()
