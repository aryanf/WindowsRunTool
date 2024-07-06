from message import (MainCommandMessage, SubCommandMessage)
from pyvda import AppView, get_apps_by_z_order, VirtualDesktop, get_virtual_desktops
import win32gui
import win32con
import psutil
import win32process, win32gui
import curses_terminal


def main(message: MainCommandMessage):
    '''
Move the latest select window to another virtual desktop
The number of target virtual desktop is the message.num, the default value is 1
'''
    current_desktop = VirtualDesktop.current()
    apps = current_desktop.apps_by_z_order()
    window_to_move = apps[3]
    target_desktop = VirtualDesktop(int(message.num )- 1)
    window_to_move.move(target_desktop)
    
