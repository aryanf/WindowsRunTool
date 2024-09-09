from pyvda import VirtualDesktop
import psutil
import win32process
import ctypes
import pythoncom
import win32com.client


def get_directory_path():
    explorer = get_explorer_window()
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
            return current_path
    return None


def get_selected_file_path():
    explorer = get_explorer_window()
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
                return selected_path
    return None


def get_explorer_window():
    current_desktop = VirtualDesktop.current()
    apps = current_desktop.apps_by_z_order()
    app_filtered = []
    for app in apps:
        try:
            _,pid = win32process.GetWindowThreadProcessId(app.hwnd)
            process = psutil.Process(pid)
            if(process.name() == 'cmd.exe'):
                continue
            app_filtered.append([process.name(), app])
        except:
            app_filtered.append(["Unknown", app])

    if app_filtered[0][0] == 'explorer.exe':
        return app_filtered[0][1]
    else:
        return None
    

def get_window_title(app):
    explorer = app.hwnd
    length = ctypes.windll.user32.GetWindowTextLengthW(explorer)
    title = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(explorer, title, length + 1)
    return title.value

