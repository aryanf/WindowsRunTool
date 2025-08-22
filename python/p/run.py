from message import (MainCommandMessage, SubCommandMessage)
import winreg as reg
import psutil
import subprocess
import os

username = os.getenv('USER') or os.getenv('LOGNAME') or os.getenv('USERNAME')
key_path = r'Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced'
slickrun_file_path = r"C:\Users\{}\AppData\Roaming\SlickRun\SlickRun.ini".format(username.lower())

def main(message:MainCommandMessage):
    print('run main')
    try:
        if _get_state_slick_winkey_r():
            print("SlickRun Win+R is enabled.")
            _run_disable()
        else:
            print("SlickRun Win+R is disabled.")
            _run_enable()
    except Exception as e:
        print(f"An error occurred: {e}")
        input()

def enable(message:SubCommandMessage):
    _run_enable()

def _run_enable():
    print('run enable')
    try:
        _disable_windows_winkey_r()
        _enable_slick_winkey_r()
        _kill_slick_process()
        _run_slick_process()
    except Exception as e:
        print(f"An error occurred: {e}")
        input()


def disable(message:SubCommandMessage):
    _run_disable()

def _run_disable():
    print('run disable')
    try:
        _enable_windows_winkey_r()
        _disable_slick_winkey_r()
        _kill_slick_process()
        _run_slick_process()
    except Exception as e:
        print(f"An error occurred: {e}")
        input()

def _kill_slick_process():
    process_name = "sr.exe"
    # Iterate over all running processes
    process_names = [proc.info['name'] for proc in psutil.process_iter(['name'])]
    for proc in psutil.process_iter(['pid', 'name']):
        # Check if process name matches
        if proc.info['name'] == process_name:
            # Kill the process
            proc.kill()
            print(f"Killed process {process_name} with PID {proc.info['pid']}")
            break
    else:
        print(f"No process named {process_name} found.")

def _run_slick_process():
    # Path to the executable
    exe_path = r"C:\Program Files\SlickRun\sr.exe"

    # Run the executable
    try:
        process = subprocess.Popen([exe_path])
        print("SlickRun started successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to start SlickRun. Error: {e}")
    except FileNotFoundError:
        print(f"The file {exe_path} was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def _disable_windows_winkey_r():
    # Open the registry key with write access
    registry_key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_WRITE)
    # Create a new DWORD value named "DisabledHotkeys"
    reg.SetValueEx(registry_key, "DisabledHotkeys", 0, reg.REG_EXPAND_SZ, 'R')
    # Close the registry key
    reg.CloseKey(registry_key)
    print("Registry key updated successfully.")

def _enable_windows_winkey_r():
    # Open the registry key with write access
    registry_key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_WRITE)
    # Delete the DisabledHotkeys value
    reg.DeleteValue(registry_key, "DisabledHotkeys")
    # Close the registry key
    reg.CloseKey(registry_key)
    print("Registry key updated successfully.")

def _get_state_slick_winkey_r():
    # Read the file
    with open(slickrun_file_path, 'r') as file:
        lines = file.readlines()

    # Find the BringUpModifier value
    for line in lines:
        if "BringUpModifier" in line:
            return True if int(line.split('=')[1]) == 8 else False

def _enable_slick_winkey_r():
    # Read the file
    with open(slickrun_file_path, 'r') as file:
        lines = file.readlines()

    # Modify the BringUpModifier value
    with open(slickrun_file_path, 'w') as file:
        for line in lines:
            if "BringUpModifier" in line:
                file.write("BringUpModifier=8\n")
            else:
                file.write(line)

def _disable_slick_winkey_r():
    # Read the file
    with open(slickrun_file_path, 'r') as file:
        lines = file.readlines()

    # Modify the BringUpModifier value
    with open(slickrun_file_path, 'w') as file:
        for line in lines:
            if "BringUpModifier" in line:
                file.write("BringUpModifier=1\n")
            else:
                file.write(line)