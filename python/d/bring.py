from message import (MainCommandMessage, SubCommandMessage)
from pyvda import AppView, get_apps_by_z_order, VirtualDesktop, get_virtual_desktops
import win32gui
import win32con
import psutil
import win32process, win32gui
import curses_terminal



def _find_app(app_name):
    desktops = get_virtual_desktops()
    for _, desktop in enumerate(desktops):
        apps = desktop.apps_by_z_order()
        for app in apps:
            try:
                _,pid = win32process.GetWindowThreadProcessId(app.hwnd)
                process = psutil.Process(pid)
                if app_name.lower() in process.name().lower():
                    return app
            except:
                return None
    return None


def main(message: MainCommandMessage):
    '''
d default function to go to another virtual desktop
The number of the desktop is the message.num, the default value is 1
'''
    current_desktop = VirtualDesktop.current()
    switch = message.switch_1
    if switch:
        app = _find_app(switch)
        if app:
            app.move(current_desktop)
            app.set_focus()
        else:
            print('App not found')
    else:
        print('Switch is not provided')