from message import (RunInfoMessage, get_open_source_app_dir)
import subprocess
import pyperclip
import win32gui
import win32con
import curses_terminal
import validators
import os

hwnd = win32gui.GetForegroundWindow()
win32gui.SetWindowPos(hwnd,win32con.HWND_TOP,1,1,900,800,0)

qdir_path = os.path.join(get_open_source_app_dir(), 'Q-Dir', 'Q-Dir_x64.exe')
chrome_path = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
edge_path = 'C:\\Program Files (x86)\\Microsoft\\edge\\Application\\msedge.exe'
notepad_path = os.path.join(get_open_source_app_dir(), 'Notepad++64', 'notepad++.exe')
browser_mapping = {
    'c': 'chrome',
    'ch': 'chrome',
    'chrome': 'chrome',
    'chmoe': 'chrome',
    'chrom': 'chrome',
    'e': 'edge',
    'ed': 'edge',
    'ege': 'edge',
    'edg': 'edge',
    'edge': 'edge'
}

def main(message: RunInfoMessage, info_dir: str, user_path: str):
    # get directory of the info_path
    if message.command and message.switch_1 and message.switch_2:
        _show_dir(os.path.join(info_dir, message.command, message.switch_1, message.switch_2))
    elif message.command and message.switch_1:
        _show_dir(os.path.join(info_dir, message.command, message.switch_1))
    elif message.command:
        _show_dir(os.path.join(info_dir, message.command))
    else:
        _show_dir(info_dir)


def _show_dir(current_dir, scrollable=True):
    def add_to_options(items, color, separator=True):
        """Helper function to add items and their colors to the list."""
        options.extend([(item, color) for item in items if item])
        if separator and items:
            options.append(('------', curses_terminal.COLOR_WHITE))

    def add_to_commands(items, color, separator=True):
        """Helper function to add items and their colors to the list."""
        commands.extend([(item, color) for item in items if item])
        if separator and items:
            commands.append(('------', curses_terminal.COLOR_WHITE))

    dirs = []
    files = []
    index_content = []

    # Traverse the directory once and separate files and directories
    for entry in os.scandir(current_dir):
        if entry.is_dir() and entry.name != '.stfolder':
            dirs.append(entry.name)
        elif entry.is_file():
            if entry.name == 'index.diff':
                with open(entry.path, 'r', encoding='utf-8') as f:
                    index_content = [line.strip() for line in f if line.strip()]
            else:
                files.append(entry.name)

    # Prepare the list and colors for display
    options = [('..', curses_terminal.COLOR_WHITE)]

    # Add index content, remove starting and initial spaces, and colorize lines
    # change line in index_content
    for i in range(len(index_content)):
        line = index_content[i]
        if line.startswith('Index:'):
            line = line[6:].strip()
            index_content[i] = line
            options.append((line, curses_terminal.COLOR_RED))
        elif line.startswith('---'):
            line = line[3:].strip()
            index_content[i] = line
            options.append((line, curses_terminal.COLOR_GREEN))
        elif line.startswith('@'):
            line = line[1:].strip()
            index_content[i] = line
            options.append((line, curses_terminal.COLOR_BLUE))
        elif line.startswith('+'):
            line = line[1:].strip()
            index_content[i] = line
            options.append((line, curses_terminal.COLOR_11))
        elif line.startswith('-'):
            line = line[1:].strip()
            index_content[i] = line
            options.append((line, curses_terminal.COLOR_12))
        else:
            line = line.strip()
            options.append((line, curses_terminal.COLOR_WHITE))

    if index_content:
        options.append(('------', curses_terminal.COLOR_WHITE))

    # Add directories and files
    add_to_options(dirs, curses_terminal.COLOR_YELLOW)
    add_to_options(files, curses_terminal.COLOR_MAGENTA)
    
    commands = []
    add_to_commands(['open dir (o)', 'open index (i)'], curses_terminal.COLOR_BLUE, separator=False)
    add_to_commands(['create dir (cd)', 'create index (ci)'], curses_terminal.COLOR_GREEN, separator=False)
    add_to_commands(['exit (e)'], curses_terminal.COLOR_RED, separator=False)

    # Show the menu
    i, cmd = curses_terminal.show(options_colors=options, commands_colors=commands, enumerating=True,
                                  zero_indexed=True, scrollable=scrollable, default_selected_index=1)

    # Handle user commands
    if cmd in index_content:
        if _is_valid_url(cmd):
            browser = browser_mapping.get(cmd, 'chrome')
            subprocess.Popen([chrome_path if browser == 'chrome' else edge_path, cmd], shell=True)
        pyperclip.copy(cmd)
    elif cmd in dirs:
        _show_dir(os.path.join(current_dir, cmd))
    elif cmd == '..':
        _show_dir(os.path.dirname(current_dir))
    elif cmd in files:
        file_path = os.path.join(current_dir, cmd)
        if cmd.lower().endswith(('.diff', '.txt')):
            subprocess.Popen(['start', notepad_path, file_path], shell=True)
        else:
            os.startfile(file_path)
    elif cmd in ['open dir (o)', 'o']:
        subprocess.Popen(['start', qdir_path, current_dir], shell=True)
    elif cmd in ['open index (i)', 'i']:
        subprocess.Popen(['start', notepad_path, os.path.join(current_dir, 'index.diff')], shell=True)
    elif cmd in ['create dir (cd)', 'cd']:
        new_dir = curses_terminal.get_user_input('Enter new directory name: ')
        if new_dir:
            os.makedirs(os.path.join(current_dir, new_dir), exist_ok=True)
    elif cmd in ['create index (ci)', 'ci']:
        index_path = os.path.join(current_dir, 'index.diff')
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write('')
        subprocess.Popen(['start', notepad_path, index_path], shell=True)
    elif cmd in ['exit', 'exit (e)', 'quit', 'q', 'e']:
        exit()
    _show_dir(current_dir, scrollable)


def _is_valid_url(url):
    if url.startswith("http://localhost") or url.startswith("https://localhost"):
        return True
    return validators.url(url)