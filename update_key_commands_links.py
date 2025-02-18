import os



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
            if file != 'install.bat' and any(file.endswith(ext) for ext in extensions):
                # Construct the full path to the file
                file_path = os.path.join(directory, file)
                # Remove the file
                os.remove(file_path)
                print(f"Removed: {file_path}")
    except Exception as e:
        print(f"Error: {e}")


def update_key_commands_links():
    print('Updating key commands links...')
    import win32com.client
    current_dir = os.getcwd()
    # Remove all bat and lnk files in the current directory
    remove_files_with_extension(current_dir, ['.bat', '.lnk'])
    # Get all key directories un {current_dir}/python
    key_commands = get_first_level_directory_names(os.path.join(current_dir, 'python'))
    # Define the command
    print(f'key commands: {key_commands}')
    try:
        for key_command in key_commands:
            print(f'Creating bat and shortcut for {key_command}')
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
                # Create bat file
                with open(bat_file_path, 'w') as bat_file:
                    bat_file.write(bat_content)

                # Create a shortcut to bat
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(shortcut_file_path)
                shortcut.Targetpath = bat_file_path
                shortcut.save()

                print(f'Successfully created {key_command} bat and shortcut in {current_dir}.')
    except Exception as e:
        print(f'An error occurred: {e}')
        raise e

if __name__ == '__main__':
    update_key_commands_links()