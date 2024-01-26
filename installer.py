import os
import win32com.client
from python.env_var_utils import prepend_env

key_commands = ['u', 'i', 'o']

current_dir = os.getcwd()

# This is going to add current directory to path env var
# If you face a problem here, comment this code and add it manually
prepend_env('Path', [
    current_dir
    ])

for key_command in key_commands:
    bat_file_path = os.path.join(current_dir, f'{key_command}.bat')
    shortcut_file_path = os.path.join(current_dir, f'{key_command}.lnk')
    python_script_path = os.path.join(current_dir, 'python', 'run.py')
    directory_path = os.path.join(current_dir, 'python', key_command)

    # Check if bat and shortcut already exist
    if os.path.exists(bat_file_path) and os.path.exists(shortcut_file_path):
        print('bat and shortcut already exist. Skipping creation.')
    else:
        bat_content = f'''@echo off
Set "base={current_dir}"
if ["%~1"]==[""] (
	python "%base%/python/run.py" {key_command}
) else if ["%~2"]==[""] (
	python "%base%/python/run.py" {key_command} %1
) else if ["%~3"]==[""] (
	python "%base%/python/run.py" {key_command} %1 %2
) else if ["%~4"]==[""] (
	python "%base%/python/run.py" {key_command} %1 %2 %3
) else if ["%~5"]==[""]  (
	python "%base%/python/run.py" {key_command} %1 %2 %3 %4
) else if ["%~6"]==[""]  (
	python "%base%/python/run.py" {key_command} %1 %2 %3 %4 %5
) else  (
	python "%base%/python/run.py" {key_command} %1 %2 %3 %4 %5 %6
)
'''

        # Create bat file
        with open(bat_file_path, 'w') as bat_file:
            bat_file.write(bat_content)

        # Create a shortcut to bat
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_file_path)
        shortcut.Targetpath = bat_file_path
        shortcut.save()

        print(f'Successfully created bat and shortcut in {current_dir}.')

    if not os.path.exists(directory_path):
        # Create the directory
        os.makedirs(directory_path)
        print(f"Directory '{directory_path}' created.")
    else:
        print(f"Directory '{directory_path}' already exists.")
