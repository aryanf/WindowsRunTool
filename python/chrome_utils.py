import time
import pyautogui
from window_utils import get_most_top_window_of_process_name
import win32gui
import win32con
import threading


def auto_chrome(timer_list_title_mouse_dic):
    background_thread = threading.Thread(target=run_background_chrome_check, args=(timer_list_title_mouse_dic,))
    background_thread.daemon = True  # This makes the thread exit when the main program exits
    background_thread.start()
    return


def run_background_chrome_check(timer_list_title_mouse_dic):
    timer = timer_list_title_mouse_dic['timer']
    for i in range(timer):
        time.sleep(1)
        try:
            target_hwnd, process_nam, title, runner_hwnd = get_most_top_window_of_process_name('chrome.exe')
            #print(target_hwnd, process_nam, title, runner_hwnd)
        except Exception as e:
            print(e)
            title = ''
        for title_mouse in timer_list_title_mouse_dic['title_mouse']:
            if title.startswith(title_mouse['title']):
                if win32gui.IsIconic(target_hwnd):
                    win32gui.ShowWindow(target_hwnd, win32con.SW_RESTORE)
                win32gui.SetWindowPos(target_hwnd, win32con.HWND_TOP, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                win32gui.SetForegroundWindow(target_hwnd)
                pyautogui.click(title_mouse['mouse'])