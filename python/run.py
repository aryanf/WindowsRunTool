import sys
import win32com.client 
import os
from help_utils import(print_all_commands_help)
import importlib
import subprocess
from time import sleep
from message import (
    RunOperationMessage,
    RunUrlMessage,
    RunInfoMessage, 
    to_main_command_message, 
    to_sub_command_message,
    get_all_env,
    get_open_source_app_dir)

json_edit_app_path = os.path.join(get_open_source_app_dir(), 'JsonEdit', 'JSONedit.exe')
notepad_app_path = os.path.join(get_open_source_app_dir(), 'Notepad++64', 'notepad++.exe')

HELP = False
DEBUG = False
EDIT = False


def continue_terminal():
    user_input = input()    
    process = subprocess.Popen(user_input, shell=True)
    process.communicate()

def debug(log):
    if(DEBUG):
        print(log)

def get_target_path(lnk_file_path):
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(lnk_file_path)
    print(shortcut.Targetpath)
    return shortcut.Targetpath

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    
def find_and_remove_command(input_list):
    if len(input_list)>=2:
        return input_list[0], input_list[1:]
    elif len(input_list)==1:
        return input_list[0], []
    else:
        return None, input_list
    
def find_and_remove_edit(input_list):
    edit_flag = False
    new_list = []
    for item in input_list:
        if item == '-edit':
            edit_flag = True
        else:
            new_list.append(item)
    return edit_flag, new_list

def find_and_remove_help(input_list):
    help_flag = False
    new_list = []
    for item in input_list:
        if item == '-help':
            help_flag = True
        else:
            new_list.append(item)
    return help_flag, new_list

def find_and_remove_debug(input_list):
    debug_flag = False
    new_list = []
    for item in input_list:
        if item == '-debug':
            debug_flag = True
        else:
            new_list.append(item)
    return debug_flag, new_list

def find_and_remove_env(input_list):
    env_list = get_all_env()
    env = None
    new_list = []
    for item in input_list:
        if item in env_list and env is None:
            env = item
        else:
            new_list.append(item)
    if env is not None:
        return env, new_list
    else:
        return env_list[0], input_list
    
def find_and_remove_operator(input_list):
    operator = 'and'
    new_list = []
    for item in input_list:
        if item == 'or':
            operator = 'or'
        elif item == 'and':
            operator = 'and'
        else:
            new_list.append(item)
    return operator, new_list
    
def find_and_remove_first_int(input_list):
    found_int = None
    new_list = []
    for item in input_list:
        if is_int(item) and found_int is None:
            found_int = item
        else:
            new_list.append(item)
    if found_int is not None:
        return found_int, new_list
    else:
        return 0, input_list

def parse_args_operation_message(arg1, arg2, arg3='', arg4='', arg5='', arg6='', arg7='') -> RunOperationMessage:
    global HELP
    global DEBUG
    global EDIT
    key = arg1
    params = [arg for arg in [arg2, arg3, arg4, arg5, arg6, arg7] if arg != ""]
    HELP, params = find_and_remove_help(params)
    DEBUG, params = find_and_remove_debug(params)
    EDIT, params = find_and_remove_edit(params)
    count, params = find_and_remove_first_int(params)
    command, params = find_and_remove_command(params)
    env, params = find_and_remove_env(params)
    debug(f'parameters: {params}')
    switch_1 = params[0] if len(params) > 0 else ''
    switch_2 = params[1] if len(params) > 1 else ''
    switch_3 = params[2] if len(params) > 2 else ''
    return RunOperationMessage(key, command, env, count, switch_1, switch_2, switch_3)

def parse_args_url_message(arg1, arg2, arg3='', arg4='', arg5='', arg6='', arg7='') -> RunUrlMessage:
    global HELP
    global DEBUG
    global EDIT
    key = arg1
    params = [arg for arg in [arg2, arg3, arg4, arg5, arg6, arg7] if arg != ""]
    HELP, params = find_and_remove_help(params)
    DEBUG, params = find_and_remove_debug(params)
    EDIT, params = find_and_remove_edit(params)
    command, params = find_and_remove_command(params)
    env, params = find_and_remove_env(params)
    operator, params = find_and_remove_operator(params)
    count, params = find_and_remove_first_int(params)    # at this point switch and some search params are in params list
    debug(f'parameters: {params}')
    switch_1 = params[0] if len(params) > 0 else ''
    switch_2 = params[1] if len(params) > 1 else ''
    switch_3 = params[2] if len(params) > 2 else ''
    return RunUrlMessage(key, command, env, count, operator, switch_1, switch_2, switch_3)

def parse_args_info_message(arg1, arg2, arg3='', arg4='', arg5='', arg6='', arg7='') -> RunInfoMessage:
    global HELP
    global DEBUG
    global EDIT
    key = arg1
    params = [arg for arg in [arg2, arg3, arg4, arg5, arg6, arg7] if arg != ""]
    HELP, params = find_and_remove_help(params)
    EDIT, params = find_and_remove_edit(params)
    command, params = find_and_remove_command(params)
    debug(f'parameters: {params}')
    switch_1 = params[0] if len(params) > 0 else ''
    switch_2 = params[1] if len(params) > 1 else ''
    switch_3 = params[2] if len(params) > 2 else ''
    return RunInfoMessage(key, command, switch_1, switch_2, switch_3)

def run_command(arg1='', arg2='', arg3='', arg4='', arg5='', arg6='', arg7=''):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
    key_dir = os.path.join(current_dir, arg1)
    user_file_path = os.path.join(root_dir, 'user_configuration.json')
    url_file_path = os.path.join(key_dir, 'urls.json')
    info_file_path = os.path.join(key_dir, 'info.diff')
    info_link_file_path = os.path.join(key_dir, 'info.lnk')
    if os.path.exists(info_file_path):
        runMessage: RunInfoMessage = parse_args_info_message(arg1, arg2, arg3, arg4, arg5, arg6, arg7)
        run_info(runMessage, current_dir, key_dir, info_file_path, user_file_path)
    if os.path.exists(info_link_file_path):
        runMessage: RunInfoMessage = parse_args_info_message(arg1, arg2, arg3, arg4, arg5, arg6, arg7)
        info_file_path = get_target_path(info_link_file_path)
        run_info(runMessage, current_dir, key_dir, info_file_path, user_file_path)
    elif os.path.exists(url_file_path):
        runMessage: RunUrlMessage = parse_args_url_message(arg1, arg2, arg3, arg4, arg5, arg6, arg7)
        run_url(runMessage, current_dir, key_dir, url_file_path, user_file_path)
    else:
        runMessage: RunOperationMessage = parse_args_operation_message(arg1, arg2, arg3, arg4, arg5, arg6, arg7)
        run_operation(runMessage, current_dir, key_dir, user_file_path)


def run_info(runMessage: RunInfoMessage, current_dir: str, key_dir: str, info_file_path: str, user_file_path: str):
    if HELP or EDIT:
        subprocess.Popen(['start', notepad_app_path, '-ldiff', info_file_path], shell=True)
    else:
        sys.path.append(current_dir)
        try:
            x_module = importlib.import_module(f'parse_info')
            getattr(x_module, "main")(runMessage, info_file_path, user_file_path)
        except ImportError as e:
            print(e)
            continue_terminal()
        finally:
            sys.path.remove(current_dir)

def run_url(runMessage: RunUrlMessage, current_dir: str, key_dir: str, url_file_path: str, user_file_path: str):
    if HELP or EDIT:
        subprocess.Popen([json_edit_app_path, url_file_path])
    else:
        sys.path.append(current_dir)
        try:
            x_module = importlib.import_module(f'parse_urls')
            getattr(x_module, "main")(runMessage, url_file_path, user_file_path)
        except ImportError as e:
            print(e)
            continue_terminal()
        finally:
            sys.path.remove(current_dir)

def run_operation(runMessage: RunOperationMessage, current_dir: str, key_dir: str, user_file_path: str):
    if runMessage.command == None:
        if HELP:
            print_all_commands_help(key_dir, runMessage.key)
            continue_terminal()
        else:
            runMessage.command = '_'
            continue_with_command(runMessage, current_dir, key_dir)
    else:
        continue_with_command(runMessage, current_dir, key_dir)

def continue_with_command(runMessage: RunOperationMessage, current_dir, key_dir):
    script_command = f"{runMessage.command}.py"
    script_path = os.path.join(key_dir, script_command)
    if os.path.exists(script_path):
        sys.path.append(current_dir)
        try:
            # Import the X module
            x_module = importlib.import_module(f'{runMessage.key}.{runMessage.command}')
            if (not runMessage.command.startswith('_') and 
                hasattr(x_module, runMessage.switch_1) and callable(getattr(x_module, runMessage.switch_1))):
                # Call Z function
                if HELP:
                    print(getattr(x_module, runMessage.switch_1).__doc__)
                    continue_terminal()
                else:
                    getattr(x_module, runMessage.switch_1)(to_sub_command_message(runMessage))
            else:
                if HELP:
                    print(getattr(x_module, "main").__doc__)
                    continue_terminal()
                else:
                    getattr(x_module, "main")(to_main_command_message(runMessage))
        except ImportError as e:
            print(e)
            continue_terminal()
        except Exception as e:
            print(e)
            continue_terminal()
        finally:
            # Remove the path to directory Y from the system path
            sys.path.remove(current_dir)
    elif os.path.exists(os.path.join(key_dir, "_.py")):
        runMessage.switch_1 = runMessage.command
        runMessage.command = '_'
        continue_with_command(runMessage, current_dir, key_dir)
    else:
        print(f"Error: {runMessage.command} not found ...")
        sleep(2)
        subprocess.Popen([runMessage.command], shell=True)

def entry():
    if len(sys.argv) == 1:
        print('key and command are needed, like:')
        print('o shot ...')
        print('u git ...')
    elif len(sys.argv) == 2:
        run_command(sys.argv[1])
    elif len(sys.argv) == 3:
        run_command(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 4:
        run_command(sys.argv[1], sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 5:
        run_command(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    elif len(sys.argv) == 6:
        run_command(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif len(sys.argv) == 7:
        run_command(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
    elif len(sys.argv) == 8:
        run_command(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])
    else:
        print('Error: too many parameters')

entry()