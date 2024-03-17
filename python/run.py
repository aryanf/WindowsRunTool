import sys
import os
from help_utils import(print_all_commands_help)
import importlib
from itertools import zip_longest
import subprocess
from time import sleep
from message import (
    RunOperationMessage,
    RunUrlFetchMessage,
    RunInfoFetchMessage, 
    to_main_command_message, 
    to_sub_command_message, 
    get_open_source_app_dir)

json_edit_app_path = os.path.join(get_open_source_app_dir(), 'JsonEdit', 'JSONedit.exe')
notepad_app_path = os.path.join(get_open_source_app_dir(), 'Notepad++64', 'notepad++.exe')

HELP = False
DEBUG = False
ENV_LIST = ['dev', 'staging', 'prod']  # First env item is the default


def continue_terminal():
    user_input = input()    
    process = subprocess.Popen(user_input, shell=True)
    process.communicate()

def debug(log):
    if(DEBUG):
        print(log)

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
    env = None
    new_list = []
    for item in input_list:
        if item in ENV_LIST and env is None:
            env = item
        else:
            new_list.append(item)
    if env is not None:
        return env, new_list
    else:
        return ENV_LIST[0], input_list
    
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
        return 1, input_list

def parse_args_get_operation_message(arg1, arg2, arg3='', arg4='', arg5='', arg6='', arg7='') -> RunOperationMessage:
    global HELP
    global DEBUG
    key = arg1
    params = [arg for arg in [arg2, arg3, arg4, arg5, arg6, arg7] if arg != ""]
    HELP, params = find_and_remove_help(params)
    DEBUG, params = find_and_remove_debug(params)
    command, params = find_and_remove_command(params)
    env, params = find_and_remove_env(params)
    count, params = find_and_remove_first_int(params)    # at this point switch and some search params are in params list
    debug(f'parameters: {params}')
    switch_1 = params[0] if len(params) > 0 else ''
    switch_2 = params[1] if len(params) > 1 else ''
    switch_3 = params[2] if len(params) > 2 else ''
    return RunOperationMessage(key, command, env, count, switch_1, switch_2, switch_3)

def parse_args_get_url_fetch_message(arg1, arg2, arg3='', arg4='', arg5='', arg6='', arg7='') -> RunUrlFetchMessage:
    global HELP
    global DEBUG
    key = arg1
    params = [arg for arg in [arg2, arg3, arg4, arg5, arg6, arg7] if arg != ""]
    HELP, params = find_and_remove_help(params)
    DEBUG, params = find_and_remove_debug(params)
    command, params = find_and_remove_command(params)
    env, params = find_and_remove_env(params)
    count, params = find_and_remove_first_int(params)    # at this point switch and some search params are in params list
    debug(f'parameters: {params}')
    switch_1 = params[0] if len(params) > 0 else ''
    switch_2 = params[1] if len(params) > 1 else ''
    switch_3 = params[2] if len(params) > 2 else ''
    return RunUrlFetchMessage(key, command, env, count, switch_1, switch_2, switch_3)

def parse_args_get_info_fetch_message(arg1, arg2, arg3='', arg4='', arg5='', arg6='', arg7='') -> RunInfoFetchMessage:
    global HELP
    global DEBUG
    key = arg1
    params = [arg for arg in [arg2, arg3, arg4, arg5, arg6, arg7] if arg != ""]
    HELP, params = find_and_remove_help(params)
    command, params = find_and_remove_command(params)
    debug(f'parameters: {params}')
    switch_1 = params[0] if len(params) > 0 else ''
    switch_2 = params[1] if len(params) > 1 else ''
    switch_3 = params[2] if len(params) > 2 else ''
    return RunInfoFetchMessage(key, command, switch_1, switch_2, switch_3)

def command(arg1='', arg2='', arg3='', arg4='', arg5='', arg6='', arg7=''):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    key_dir = os.path.join(current_dir, arg1)
    config_file_path = os.path.join(key_dir, 'web_configuration.json')
    info_file_path = os.path.join(key_dir, 'info.diff')
    if os.path.exists(info_file_path):
        runMessage: RunInfoFetchMessage = parse_args_get_info_fetch_message(arg1, arg2, arg3, arg4, arg5, arg6, arg7)
        run_info(runMessage, current_dir, key_dir, info_file_path)
    elif os.path.exists(config_file_path):
        runMessage: RunUrlFetchMessage = parse_args_get_url_fetch_message(arg1, arg2, arg3, arg4, arg5, arg6, arg7)
        run_url(runMessage, current_dir, key_dir, config_file_path)
    else:
        runMessage: RunOperationMessage = parse_args_get_operation_message(arg1, arg2, arg3, arg4, arg5, arg6, arg7)
        run_operation(runMessage, current_dir, key_dir)


def run_info(runMessage: RunInfoFetchMessage, current_dir: str, key_dir: str, info_file_path: str):
    if HELP:
        subprocess.Popen(['start', notepad_app_path, '-ldiff', info_file_path], shell=True)
    else:
        sys.path.append(current_dir)
        try:
            x_module = importlib.import_module(f'parse_info')
            getattr(x_module, "main")(runMessage, info_file_path)
        except ImportError as e:
            print(e)
            continue_terminal()
        finally:
            sys.path.remove(current_dir)

def run_url(runMessage: RunUrlFetchMessage, current_dir: str, key_dir: str, config_file_path: str):
    if HELP:
        subprocess.Popen([json_edit_app_path, config_file_path])
    else:
        sys.path.append(current_dir)
        try:
            x_module = importlib.import_module(f'parse_browser_config')
            getattr(x_module, "main")(runMessage, config_file_path)
        except ImportError as e:
            print(e)
            continue_terminal()
        finally:
            sys.path.remove(current_dir)

def run_operation(runMessage: RunOperationMessage, current_dir: str, key_dir: str):
    if runMessage.command == None:
        if HELP:
            print_all_commands_help(key_dir, runMessage.key)
            continue_terminal()
        else:
            print('Error: command should be provided ...')
            continue_terminal()
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
        finally:
            # Remove the path to directory Y from the system path
            sys.path.remove(current_dir)
    else:
        print(f"Error: {runMessage.command} not found in {key_dir}, running default Windows command ...")
        sleep(1)
        subprocess.Popen([runMessage.command], shell=True)

def entry():
    if len(sys.argv) == 1:
        print('key and command are needed, like:')
        print('p copy ...')
        print('l send ...')
    elif len(sys.argv) == 2:
        command(sys.argv[1])
    elif len(sys.argv) == 3:
        command(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 4:
        command(sys.argv[1], sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 5:
        command(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    elif len(sys.argv) == 6:
        command(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif len(sys.argv) == 7:
        command(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
    elif len(sys.argv) == 8:
        command(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])
    else:
        print('Error: too many parameters')

entry()