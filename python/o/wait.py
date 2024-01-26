from message import (MainCommandMessage, SubCommandMessage)
import pyautogui
import time


def main(message: MainCommandMessage):
    '''
Mouse clicking on screen repeatedly. Coordination, printed message and time interval can be changed in wait.main()
'''
    locs = [(1000, 1050), (1001,1050)]
    time_period = 100
    cur = 0
    while True:
        print('waiting ....')
        cur = (cur + 1) % 2
        pyautogui.moveTo(*locs[cur])
        pyautogui.click(*locs[cur])
        time.sleep(time_period)