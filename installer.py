import os
import subprocess



def get_first_level_directory_names(path):
    try:
        # List all entries in the directory
        entries = os.listdir(path)
        # Filter out entries that are directories and not special directories
        directories = [entry for entry in entries if os.path.isdir(os.path.join(path, entry)) and not entry.startswith('__')]
        return directories
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    
def remove_files_with_extension(directory, extensions):
    try:
        # List all files in the directory
        files = os.listdir(directory)
        for file in files:
            # Check if the file ends with any of the specified extensions
            if any(file.endswith(ext) for ext in extensions):
                # Construct the full path to the file
                file_path = os.path.join(directory, file)
                # Remove the file
                os.remove(file_path)
                print(f"Removed: {file_path}")
    except Exception as e:
        print(f"Error: {e}")

current_dir = os.getcwd()
# Remove all bat and lnk files in the current directory
remove_files_with_extension(current_dir, ['.bat', '.lnk'])
# Get all key directories un {current_dir}/python
key_commands = get_first_level_directory_names(os.path.join(current_dir, 'python'))
# Install library dependencies

print('Installing package dependencies...')
command = 'pip install -r requirements.txt'
# Execute the command
try:
    subprocess.check_call(command, shell=True)
    print("Package installed successfully!")
except subprocess.CalledProcessError as e:
    print("An error occurred:", e)

# This is going to add current directory to path env var
# Define the command
print(f'key commands: {key_commands}')
# If you face a problem here, comment this code and add it manually
print('Adding current directory to path env var...')
import win32com.client
from python.env_var_utils import prepend_env
prepend_env('Path', [
    current_dir
    ])
print('Successfully added current directory to path env var.')
try:
    for key_command in key_commands:
        print(f'Creating bat and shortcut for {key_command}...')
        bat_file_path = os.path.join(current_dir, f'{key_command}.bat')
        shortcut_file_path = os.path.join(current_dir, f'{key_command}.lnk')
        python_script_path = os.path.join(current_dir, 'python', 'run.py')
        directory_path = os.path.join(current_dir, 'python', key_command)
        print(f'bat_file_path: {bat_file_path}')
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
            print(f'bat_content: {bat_content}')
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
except Exception as e:
    print(f'An error occurred: {e}')
    raise e