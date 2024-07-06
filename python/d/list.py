from message import (MainCommandMessage, SubCommandMessage)
from pyvda import AppView, get_apps_by_z_order, VirtualDesktop, get_virtual_desktops
import win32gui
import win32con
import psutil
import win32process, win32gui
import curses_terminal


def _get_desktop(current_desktop: VirtualDesktop):
    desktops = get_virtual_desktops()
    desktop_names = [d.name for d in get_virtual_desktops()]
    i, cmd = curses_terminal.show(options=desktop_names, enumerating=True, zero_indexed=False, info=f'Current Desktop: {current_desktop.name}')
    if cmd == 'exit' or cmd == 'q' or cmd == 'quit' or cmd == 'e':
        exit()
    selected_desktop = desktops[i]
    _get_apps(selected_desktop)

def _get_apps(selected_desktop: VirtualDesktop):
    app_names = ['go', '..']
    apps = selected_desktop.apps_by_z_order()
    for app in apps:
        try:
            _,pid = win32process.GetWindowThreadProcessId(app.hwnd)
            process = psutil.Process(pid)
            app_names.append(process.name())
        except:
            app_names.append("Unknown")
    i, cmd = curses_terminal.show(options=app_names, enumerating=True, zero_indexed=False, info=f'Selected Desktop: {selected_desktop.name}')
    if cmd == 'exit' or cmd == 'q' or cmd == 'quit' or cmd == 'e':
        exit()
    if i == 0:
        VirtualDesktop.go(selected_desktop)
        exit()
    elif i == 1:
        _get_desktop(selected_desktop)
    else:
        desktops = get_virtual_desktops()
        desktop_names = [d.name for d in get_virtual_desktops()]
        j, cmd = curses_terminal.show(options=desktop_names, enumerating=True, zero_indexed=False, info=f'Move {app_names[i]} to other desktop')
        target_desktop = desktops[j]
        selected_window = apps[i-2]
        selected_window.move(target_desktop)
        _get_apps(selected_desktop)

def main(message: MainCommandMessage):
    '''
List of all existing virtual desktops and apps
Show current virtual desktop
Go to another virtual desktop
Move app to another virtual desktop
'''
    current_desktop = VirtualDesktop.current()
    _get_desktop(current_desktop)
    #VirtualDesktop.go(selected_desktop)

    #hwnd = win32gui.GetForegroundWindow()
    #_,pid = win32process.GetWindowThreadProcessId(hwnd)
    #process = psutil.Process(pid)

    #process_name = process.name()
    #print(process_name)

    #hwnd = win32gui.GetForegroundWindow()
    #win32gui.SetWindowPos(hwnd,win32con.HWND_BOTTOM,1,1,500,300,0)
    
    
    #apps = get_apps_by_z_order()
#    current_window = apps[i]
#    target_desktop = VirtualDesktop(int(message.num))
#    current_window.move(target_desktop)
#    print(f"Moved window {current_window.hwnd} to {target_desktop.number}")
#
#    input()

def func1(message:SubCommandMessage):
    '''
Demo main func1
This is an example to create more scripts and function
'''
    print('demo func1 function')
    print(f'env: {message.env}, num: {message.num}, switch1: {message.switch_1}, switch2: {message.switch_2}')
    input()


def func2(message:SubCommandMessage):
    '''
Demo main func2
This is an example to create more scripts and function
'''
    print('demo func2 function')
    print(f'env: {message.env}, num: {message.num}, switch1: {message.switch_1}, switch2: {message.switch_2}')
    input()