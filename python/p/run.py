from message import (MainCommandMessage, SubCommandMessage)
import winreg as reg
import psutil
import subprocess
import time
import os

key_path = r'Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced'
slickrun_file_path = os.path.join(os.environ['APPDATA'], 'SlickRun', 'SlickRun.ini')
slickrun_exe_path = r"C:\Program Files\SlickRun\sr.exe"

MOD_WIN = 8   # SlickRun BringUpModifier value for the Win key
MOD_ALT = 1   # SlickRun BringUpModifier value for the Alt key


def main(message: MainCommandMessage):
    '''
Toggle Win+R between SlickRun and the Windows Run dialog
(restarts Explorer and SlickRun)
'''
    try:
        if _get_slick_modifier() == MOD_WIN:
            print("SlickRun currently owns Win+R -> switching back to Windows Run.")
            _run_disable()
        else:
            print("Windows Run currently owns Win+R -> switching to SlickRun.")
            _run_enable()
    except Exception as e:
        print(f"An error occurred: {e}")
        input()


def enable(message: SubCommandMessage):
    '''
Win+R opens SlickRun
'''
    _run_enable()


def disable(message: SubCommandMessage):
    '''
Win+R opens the Windows Run dialog
'''
    _run_disable()


def _run_enable():
    _switch(windows_owns_win_r=False, slick_modifier=MOD_WIN)
    print("Done: Win+R -> SlickRun")


def _run_disable():
    _switch(windows_owns_win_r=True, slick_modifier=MOD_ALT)
    print("Done: Win+R -> Windows Run (SlickRun on Alt+R)")


def _switch(windows_owns_win_r: bool, slick_modifier: int):
    # Stop SlickRun first so it releases its hotkey and can't overwrite the ini on exit
    _kill_process("sr.exe")
    _set_windows_win_r(windows_owns_win_r)
    _set_slick_modifier(slick_modifier)
    # Explorer reads DisabledHotkeys only at startup
    _restart_explorer()
    # Start SlickRun after Explorer so Explorer doesn't grab Win+R first
    subprocess.Popen([slickrun_exe_path])
    print("SlickRun started.")


def _kill_process(name: str):
    for proc in psutil.process_iter(['pid', 'name']):
        if (proc.info['name'] or '').lower() == name.lower():
            try:
                proc.kill()
                proc.wait(timeout=5)
                print(f"Killed {name} (PID {proc.info['pid']})")
            except psutil.Error:
                pass


def _is_running(name: str) -> bool:
    return any((p.info['name'] or '').lower() == name.lower()
               for p in psutil.process_iter(['name']))


def _restart_explorer():
    print("Restarting Explorer...")
    subprocess.run(["taskkill", "/f", "/im", "explorer.exe"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Windows usually relaunches the shell automatically; start it only if it didn't
    for _ in range(20):
        time.sleep(0.25)
        if _is_running("explorer.exe"):
            break
    else:
        subprocess.Popen(["explorer.exe"])
    time.sleep(2)  # let the shell finish registering its hotkeys


def _set_windows_win_r(enabled: bool):
    with reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_WRITE) as key:
        if enabled:
            try:
                reg.DeleteValue(key, "DisabledHotkeys")
            except FileNotFoundError:
                pass
        else:
            reg.SetValueEx(key, "DisabledHotkeys", 0, reg.REG_SZ, 'R')
    print(f"Windows Win+R {'enabled' if enabled else 'disabled'} in registry.")


def _get_slick_modifier() -> int:
    with open(slickrun_file_path, 'r') as file:
        for line in file:
            if line.startswith("BringUpModifier="):
                return int(line.split('=', 1)[1])
    return MOD_ALT


def _set_slick_modifier(modifier: int):
    with open(slickrun_file_path, 'r') as file:
        lines = file.readlines()
    with open(slickrun_file_path, 'w') as file:
        for line in lines:
            if line.startswith("BringUpModifier="):
                file.write(f"BringUpModifier={modifier}\n")
            else:
                file.write(line)
    print(f"SlickRun BringUpModifier={modifier}")
