from message import (MainCommandMessage, SubCommandMessage)
from pyvda import AppView, get_apps_by_z_order, VirtualDesktop, get_virtual_desktops
import win32gui
import win32con
import psutil
import win32process, win32gui
import curses_terminal


def main(message: MainCommandMessage):
    '''
d default function to go to another virtual desktop
The number of the desktop is the message.num, the default value is 1
'''
    desktops = get_virtual_desktops()
    selected_desktop = desktops[int(message.num) -1]
    VirtualDesktop.go(selected_desktop)