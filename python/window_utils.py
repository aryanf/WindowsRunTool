from pyvda import VirtualDesktop
import psutil
import win32process
import ctypes
import pythoncom
import win32com.client
import time
import win32gui
import win32con


def get_directory_path_of_top_file_explorer():
    '''Get the current directory of the top File Explorer window
    Returns:
    current_path (str): The path of the current directory
    runner_window (int): The handle of the runner window
    '''
    try:
        explorer, runner_window = get_top_file_explorer_window()
        if explorer is None:
            print('Cannot catch File Explorer.')
            time.sleep(3)
            return None, runner_window
        print(_get_window_title(explorer))
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


def get_selected_files_path_in_top_file_explorer():
    '''Get the paths of the selected files in the top File Explorer window
    Returns:
    file_paths (list): List of the selected file paths
    runner_window (int): The handle of the runner window
    '''
    try:
        explorer, runner_window = get_top_file_explorer_window()
        file_paths = []
        if explorer is None:
            print('Cannot catch File Explorer.')
            time.sleep(3)
            return file_paths, runner_window
        print(_get_window_title(explorer))
        hwnd = explorer.hwnd
        # Initialize COM library for the thread
        pythoncom.CoInitialize()

        # Get the Shell object
        shell = win32com.client.Dispatch("Shell.Application")
        # Iterate through all open windows
        for window in shell.Windows():
            # Check if the window matches the HWND of the foreground window
            if int(window.HWND) == int(hwnd):
                # Check if there are any selected items
                selected_items = window.Document.SelectedItems()
                if selected_items.Count > 0:
                    for item in selected_items:
                        # Return the path of each selected item
                        file_paths.append(item.Path)
                    return file_paths, runner_window
        return file_paths, runner_window
    except Exception as e:
        print(e)
        print('Cannot catch explorer window as top window')
        time.sleep(1)
        return file_paths, runner_window


def get_top_file_explorer_window():
    '''Get the top File Explorer window
    Returns:
    explorer (int): The handle of the File Explorer window, None if not found
    runner_window (int): The handle of the runner window
'''
    runner_hwnd = win32gui.GetForegroundWindow()
    win32gui.SetWindowPos(runner_hwnd, win32con.HWND_BOTTOM, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    
    current_desktop = VirtualDesktop.current()
    apps = current_desktop.apps_by_z_order()
    app_filtered = []
    for app in apps:
        try:
            _, pid = win32process.GetWindowThreadProcessId(app.hwnd)
            process = psutil.Process(pid)
            if _is_overlay_window(app, process, runner_hwnd):
                continue
            app_filtered.append([process.name(), app])
        except:
            app_filtered.append(["Unknown", app])
    win32gui.SetWindowPos(runner_hwnd,win32con.HWND_TOP,1,1,500,300,0)
    print(f'Top windows is {app_filtered[0][0]} with title {_get_window_title(app_filtered[0][1])}')
    if app_filtered[0][0] == 'explorer.exe':
        return app_filtered[0][1], runner_hwnd
    else:
        return None, runner_hwnd


def get_top_window():
    '''Get the top window
    Returns:
    top_window (int): The handle of the top window
    process_name (str): The process name of the top window
    title (str): The title of the top window
    runner_window (int): The handle of the runner window
    '''
    runner_hwnd = win32gui.GetForegroundWindow()
    win32gui.SetWindowPos(runner_hwnd, win32con.HWND_BOTTOM, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    current_desktop = VirtualDesktop.current()
    apps = current_desktop.apps_by_z_order()
    app_filtered = []
    for app in apps:
        try:
            _, pid = win32process.GetWindowThreadProcessId(app.hwnd)
            process = psutil.Process(pid)
            if _is_overlay_window(app, process, runner_hwnd):
                continue
            app_filtered.append([process.name(), app])
        except:
            app_filtered.append(["Unknown", app])
    win32gui.SetWindowPos(runner_hwnd,win32con.HWND_TOP,1,1,500,300,0)
    title = _get_window_title(app_filtered[0][1])
    print('Top windows is ', app_filtered[0][0], ' with title ', title)
    return app_filtered[0][1].hwnd, app_filtered[0][0], title, runner_hwnd


def get_most_top_window_of_process_name(process_name):
    '''Get the top window
    Input:
    process_name (str): The process name of the top window
    Returns:
    top_window (int): The handle of the top window
    process_name (str): The process name of the top window
    title (str): The title of the top window
    runner_window (int): The handle of the runner window
    '''
    runner_hwnd = win32gui.GetForegroundWindow()
    current_desktop = VirtualDesktop.current()
    apps = current_desktop.apps_by_z_order()
    app_filtered = []
    for app in apps:
        try:
            _, pid = win32process.GetWindowThreadProcessId(app.hwnd)
            process = psutil.Process(pid)
            print(process.name())
            if process.name() == process_name:
                app_filtered.append([process.name(), app])
        except:
            app_filtered.append(["Unknown", app])
    print('app_filtered', app_filtered)
    title = _get_window_title(app_filtered[0][1])
    print('Top windows is ', app_filtered[0][0], ' with title ', title)
    return app_filtered[0][1].hwnd, app_filtered[0][0], title, runner_hwnd


def get_all_windows_of_process_name(process_name):
    '''Get all windows of a process by name.
    Input:
    process_name (str): The process name of the windows to find.
    Returns:
    list of tuples: A list where each tuple contains:
        - top_window (int): The handle of the top window.
        - process_name (str): The process name of the top window.
        - title (str): The title of the top window.
        - runner_window (int): The handle of the runner window.
    '''
    runner_hwnd = win32gui.GetForegroundWindow()
    win32gui.SetWindowPos(runner_hwnd, win32con.HWND_BOTTOM, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    current_desktop = VirtualDesktop.current()
    apps = current_desktop.apps_by_z_order()
    app_filtered = []
    for app in apps:
        try:
            _, pid = win32process.GetWindowThreadProcessId(app.hwnd)
            process = psutil.Process(pid)
            if _is_overlay_window(app, process, runner_hwnd):
                continue
            if process.name() == process_name:
                app_filtered.append([process.name(), app])
        except:
            app_filtered.append(["Unknown", app])
    win32gui.SetWindowPos(runner_hwnd,win32con.HWND_TOP,1,1,500,300,0)
    return [(app[1].hwnd, app[0], _get_window_title(app[1]), runner_hwnd) for app in app_filtered]


def top_window_to_bottom():
    '''Move the top window to the bottom of the window stack'''
    top_hwnd = win32gui.GetForegroundWindow()
    win32gui.SetWindowPos(top_hwnd, win32con.HWND_BOTTOM, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)


def get_process_name_of_hwnd_window(hwnd):
    '''Get the process name of a window by its handle
    Input:
    hwnd (int): The handle of the window
    Returns:
    process_name (str): The process name of the window
    '''
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    process = psutil.Process(pid)
    return process.name()


def _get_window_title(app):
    explorer = app.hwnd
    length = ctypes.windll.user32.GetWindowTextLengthW(explorer)
    title = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(explorer, title, length + 1)
    return title.value


def _is_overlay_window(app, process, runner_hwnd):
    if app.hwnd == runner_hwnd:
        return True
    if process.name() == 'ms-teams.exe':
        return True
    if process.name() == 'explorer.exe' and win32gui.GetClassName(app.hwnd) != 'CabinetWClass':
        return True
    return False