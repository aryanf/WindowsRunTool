from message import (MainCommandMessage, SubCommandMessage)
from pyvda import AppView, get_apps_by_z_order, VirtualDesktop, get_virtual_desktops
import win32gui
import win32con
import psutil
import win32process, win32gui
import curses_terminal
import psutil

def find_substring_index(lst, input_str):
    for index, item in enumerate(lst):
        if input_str in item:
            return index
    return -1  # return -1 if the input string is not found in any item



def main(message: MainCommandMessage):
    '''
Move the latest select window to another virtual desktop
The number of target virtual desktop is the message.num
'''
    current_desktop = VirtualDesktop.current()
    apps = current_desktop.apps_by_z_order()
    app_names = []
    for app in apps:
        try:
            _,pid = win32process.GetWindowThreadProcessId(app.hwnd)
            process = psutil.Process(pid)
            app_names.append(process.name())
        except:
            app_names.append("Unknown")
    counter = 0
    for app_name in app_names:
        if 'explore' in app_name:
            counter += 1
        if 'cmd' in app_name:
            counter += 1
            break
    window_to_move = apps[counter]
    desktops = get_virtual_desktops()
    desktop_names = [d.name for d in get_virtual_desktops()]
    switch = message.switch_1
    if switch:
        idx = find_substring_index(desktop_names, switch)
        if idx == -1:
            print('Desktop not found')
            input('Press Enter to continue...')
            return
        target_desktop = desktops[idx]
    else:
        target_desktop = desktops[int(message.num)- 1]
    window_to_move.move(target_desktop)
    VirtualDesktop.go(target_desktop)

    
