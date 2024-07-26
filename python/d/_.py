from message import (MainCommandMessage, SubCommandMessage)
from pyvda import AppView, get_apps_by_z_order, VirtualDesktop, get_virtual_desktops
import win32gui
import win32con
import psutil
import win32process, win32gui
import curses_terminal


def _find_substring_index(lst, input_str):
    for index, item in enumerate(lst):
        if input_str.lower() in item.lower():
            return index
    return -1  # return -1 if the input string is not found in any item

def main(message: MainCommandMessage):
    '''
d default function to go to another virtual desktop
The number of the desktop is the message.num, the default value is 1
'''
    desktops = get_virtual_desktops()
    desktop_names = [d.name for d in get_virtual_desktops()]
    current_desktop = VirtualDesktop.current()
    num = int(message.num)
    switch = message.switch_1
    if num == 0 and not switch:
        VirtualDesktop.go(current_desktop)
    elif switch:
        idx = _find_substring_index(desktop_names, switch)
        if idx == -1:
            print('Desktop not found')
            input('Press Enter to continue...')
            return
        selected_desktop = desktops[idx]
        VirtualDesktop.go(selected_desktop)
    else:
        selected_desktop = desktops[int(message.num) -1]
        VirtualDesktop.go(selected_desktop)