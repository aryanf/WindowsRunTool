from message import (MainCommandMessage, SubCommandMessage)
from message import (MainCommandMessage, get_open_source_app_dir)
import explorer_utils
import os
import subprocess
import re
import win32gui
import win32con


app_path = os.path.join(get_open_source_app_dir(), 'RipGrep', 'rg.exe')

def main(message: MainCommandMessage):
    '''
Search in files for a pattern
Basic Usage:
rg <pattern>: Search for <pattern> in the current directory and all subdirectories.

File Type and File Path Control:
-t <filetype>: Search only files matching the specified type (e.g., rg -t py pattern for Python files).
-T <filetype>: Exclude files of the specified type.
-g <glob>: Include files that match the given glob pattern (e.g., rg -g "*.md" pattern).
-g '!<glob>': Exclude files matching the glob pattern (e.g., rg -g '!.git/*').
--iglob <glob>: Case-insensitive glob pattern.

Recursive Search and File Inclusion/Exclusion:
-u: Search hidden files and directories.
-uu: Search hidden and ignore .gitignored files.
-uuu: Search hidden, .gitignored, and .ignore files.
--hidden: Search hidden files and directories (same as -u).
--no-ignore: Do not respect .gitignore, .ignore, or other ignore files.

Pattern Matching:
-i: Case-insensitive search.
-w: Search for whole words.
-x: Search for exact matches (whole line matches).
--fixed-strings (-F): Treat the pattern as a literal string, not a regex.

Output Control:
-n: Show line numbers in output.
-H: Always show the file name in the output.
-v: Invert the match (show lines that do not match).
-c: Only show the count of matching lines per file.
-C <num>: Show num lines of context before and after matches (e.g., -C 2).
-B <num>: Show num lines of context before matches.
-A <num>: Show num lines of context after matches.
-o: Show only the matching part of the lines.
-p: Show the full path of the matched file.

Performance and Search Limits:
-m <num>: Stop searching after num matches.
--max-depth <num>: Limit the depth of directory traversal.
--threads <num>: Set the number of threads to use during search.

Binary and Encoding:
-a: Search binary files as if they were text.
--binary: Enable binary file searching.
--encoding <encoding>: Specify the text encoding (e.g., --encoding utf-8).

JSON Output:
--json: Outputs results in JSON format, which is useful for further processing with other tools.
'''
    grep_switches = []
    directory_path = ''
    if message.switch_1:
        for switch in [message.switch_1, message.switch_2, message.switch_3]:
            if switch:
                if _is_windows_path(switch):
                    directory_path = switch
                else:
                    grep_switches.append(switch)
            
        if not directory_path:
            directory_path = explorer_utils.get_directory_path()
        print(f'path: {directory_path}')
        subprocess.Popen([app_path, *grep_switches, directory_path])
        print('-----------------')
        input()
    else:    
        directory_path, runner_hwnd = explorer_utils.get_directory_path()
        win32gui.SetWindowPos(runner_hwnd,win32con.HWND_TOP,1,1,500,300,0)
        if not directory_path:
            directory_path = input('Enter search path: ')
        print(f'search path: {directory_path}')
        search_pattern = input('Enter search pattern: ')
        grep_switches = input('Enter switches: ')
        switches = grep_switches.split(' ')
        subprocess.Popen([app_path, *switches, search_pattern, directory_path])
        print('-----------------')
        input()

def _is_windows_path(path):
    """
    Determines if a given string is a valid Windows path address.
    
    Args:
        path (str): The string to check.
        
    Returns:
        bool: True if the string is a valid Windows path, False otherwise.
    """
    # Check for invalid characters in the path
    invalid_chars = r'[<>:"|?*]'
    if re.search(invalid_chars, path):
        return False

    # Check if the path is an absolute path (starts with a drive letter or \\ for UNC paths)
    if os.path.isabs(path):
        return True

    # Check for relative paths that still conform to Windows path rules
    try:
        # Normalize and check if it can be joined properly
        normalized_path = os.path.normpath(path)
        drive, tail = os.path.splitdrive(normalized_path)
        # Must have a valid drive or start with a folder
        return bool(drive) or tail.startswith(('\\', '.\\', '..\\'))
    except Exception:
        return False