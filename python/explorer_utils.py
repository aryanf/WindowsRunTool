from pyvda import VirtualDesktop
import psutil
import win32process
import ctypes
import pythoncom
import win32com.client
import time
import win32gui
import win32con


def get_directory_path():
    try:
        explorer, runner_window = get_explorer_window()
        if explorer is None:
            print('No File Explorer window on top found')
        print(get_window_title(explorer))
        hwnd = explorer.hwnd
        # Initialize COM library for the thread
        pythoncom.CoInitialize()

        # Get the Shell object
        shell = win32com.client.Dispatch("Shell.Application")

        # Iterate through all open windows
        for window in shell.Windows():
            # Check if the window matches the HWND of the foreground window
            if int(window.HWND) == hwnd:
                # Return the current directory of the File Explorer window
                current_path = window.LocationURL.replace('file:///', '').replace('/', '\\')
                return current_path, runner_window
        return None, runner_window
    except Exception as e:
        print(e)
        print('Cannot catch explorer window as top window')
        time.sleep(2)
        return None, runner_window


def get_selected_file_path():
    try:
        explorer, runner_window = get_explorer_window()
        if explorer is None:
            print('No File Explorer window on top found')
        print(get_window_title(explorer))
        hwnd = explorer.hwnd
        # Initialize COM library for the thread
        pythoncom.CoInitialize()

        # Get the Shell object
        shell = win32com.client.Dispatch("Shell.Application")

        # Iterate through all open windows
        for window in shell.Windows():
            # Check if the window matches the HWND of the foreground window
            if int(window.HWND) == hwnd:
                # Check if there are any selected items
                selected_items = window.Document.SelectedItems()
                if selected_items.Count > 0:
                    # Return the path of the first selected item
                    selected_path = selected_items.Item(0).Path
                    return selected_path, runner_window
        return None, runner_window
    except Exception as e:
        print(e)
        print('Cannot catch explorer window as top window')
        time.sleep(1)
        return None, runner_window


def get_explorer_window():
    runner_hwnd = win32gui.GetForegroundWindow()
    win32gui.SetWindowPos(runner_hwnd,win32con.HWND_BOTTOM,1,1,500,300,0)
    current_desktop = VirtualDesktop.current()
    apps = current_desktop.apps_by_z_order()
    app_filtered = []
    for app in apps:
        try:
            _,pid = win32process.GetWindowThreadProcessId(app.hwnd)
            process = psutil.Process(pid)
            app_filtered.append([process.name(), app])
        except:
            app_filtered.append(["Unknown", app])

    if app_filtered[0][0] == 'explorer.exe':
        return app_filtered[0][1], runner_hwnd
    else:
        return None, runner_hwnd
    

def get_window_title(app):
    explorer = app.hwnd
    length = ctypes.windll.user32.GetWindowTextLengthW(explorer)
    title = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(explorer, title, length + 1)
    return title.value

