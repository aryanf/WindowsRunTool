from message import (MainCommandMessage, SubCommandMessage, get_open_source_app_dir)
import subprocess
import os
import pygetwindow as gw
import time
import win32gui
import win32con
import win32ui
import win32api
import ctypes
from PIL import Image
import win32clipboard
from io import BytesIO


# Constants for getting extended window attributes
DWMWA_EXTENDED_FRAME_BOUNDS = 9

qdir_path = os.path.join(get_open_source_app_dir(), 'Q-Dir', 'Q-Dir_x64.exe')
app_dir_path = os.path.join(get_open_source_app_dir(), 'ShareX')
app_path = os.path.join(get_open_source_app_dir(), 'ShareX', 'ShareX.exe')
pinned_dir_path = os.path.join(get_open_source_app_dir(), 'ShareX', 'ShareX', 'Pinned')
# Load the DWM API
dwmapi = ctypes.windll.dwmapi


def main(message: MainCommandMessage):
    '''
Pin an area on screen
'''
    print('cutting and pinning')
    subprocess.Popen([app_path, '-PinToScreenFromScreen'])


def toggle(message:SubCommandMessage):
    windows = _get_sharex_windows()
    if windows:
        windows_inside_of_screen = [w for w in windows if win32gui.GetWindowRect(w._hWnd)[0] > 0]
        if windows_inside_of_screen:
            hide(message)
        else:
            show(message)


def hide(message:SubCommandMessage):
    '''
Hide all ShareX pinned windows by moving them off-screen.
'''
    windows = _get_sharex_windows()
    if windows:
        for window in windows:
            hwnd = window._hWnd
            # Store original position
            rect = win32gui.GetWindowRect(hwnd)
            # Move off-screen to hide
            win32gui.MoveWindow(hwnd, -3000, rect[1], rect[2] - rect[0], rect[3] - rect[1], True)
    else:
        print("No ShareX pinned windows found.")


def show(message:SubCommandMessage):
    '''
Restore all hidden windows to their original positions.'
'''
    windows = _get_sharex_windows()
    if windows:
        screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        y_offset = 0
        for window in reversed(windows):
            hwnd = window._hWnd
            # Store original position
            rect = win32gui.GetWindowRect(hwnd)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]
            # Align to the right side of the screen and stack with a height difference of 10 pixels
            win32gui.MoveWindow(hwnd, screen_width - width, y_offset, width, height, True)
            y_offset += 50


def save(message:SubCommandMessage):
    '''
Save the current cut screens to a local directory.'
'''
    # Check directory exist
    if not os.path.exists(pinned_dir_path):
        os.makedirs(pinned_dir_path)
    # Remove all files in directory before saving
    for file in os.listdir(pinned_dir_path):
        os.remove(os.path.join(pinned_dir_path, file))
    # Capture and save all pinned windows
    windows = _get_sharex_windows()
    for i, window in enumerate(windows):
        hwnd = window._hWnd
        save_path = os.path.join(pinned_dir_path, f"screenshot_{i}.png")  # BMP format for lossless quality
        _capture_window(window, hwnd, save_path)
        print(f"Captured: {save_path}")
    else:
        print("No ShareX pinned windows found.")


def load(message:SubCommandMessage):
    '''
Load the saved cut screen from a local directory.'
'''
    for i, file in enumerate(os.listdir(pinned_dir_path)):
        # save image file to clipboard
        load_path = os.path.join(pinned_dir_path, file)
        _copy_image_to_clipboard(load_path)
        time.sleep(3)
        subprocess.Popen([app_path, '-PinToScreenFromClipboard'])
        time.sleep(3)
    else:
        print("No ShareX pinned windows found.")


def _get_sharex_windows():
    """Get all ShareX pinned windows."""
    return [w for w in gw.getWindowsWithTitle("") if "ShareX" in w.title or "Pin" in w.title]


def _capture_window(window, hwnd, save_path):
    """Captures the content of a window with correct dimensions."""

    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    
    # Get extended bounds (this includes extra margins)
    rect = ctypes.wintypes.RECT()
    dwmapi.DwmGetWindowAttribute(hwnd, DWMWA_EXTENDED_FRAME_BOUNDS, ctypes.byref(rect), ctypes.sizeof(rect))

    # Corrected full dimensions including invisible borders
    client_width = rect.right - rect.left
    client_height = rect.bottom - rect.top

    # Create device context (DC) to capture the window
    hwnd_dc = win32gui.GetWindowDC(hwnd)
    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()
    save_bitmap = win32ui.CreateBitmap()

    save_bitmap.CreateCompatibleBitmap(mfc_dc, client_width, client_height)
    save_dc.SelectObject(save_bitmap)

    # Capture window content (client area)
    # (right-left, bottom-top) is the full window size, but we only want the client area
    save_dc.BitBlt((0, 0), (client_width, client_height), mfc_dc, (0, 0), win32con.SRCCOPY)

    # Save the captured bitmap as a file
    save_bitmap.SaveBitmapFile(save_dc, save_path)

    # Cleanup resources
    win32gui.DeleteObject(save_bitmap.GetHandle())
    save_dc.DeleteDC()
    mfc_dc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwnd_dc)


def _copy_image_to_clipboard(image_path):
    """Copies an image to the Windows clipboard."""
    image = Image.open(image_path)
    
    # Convert image to bitmap format required for clipboard
    output = BytesIO()
    image.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]  # BMP header fix
    output.close()

    # Open clipboard and set image data
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()