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
    if DEBUG:
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
    if input_list:
        return input_list[0], input_list[1:]
    return None, input_list
    
def find_and_remove_flag(input_list, flag):
    flag_found = flag in input_list
    new_list = [item for item in input_list if item != flag]
    return flag_found, new_list

def find_and_remove_env(input_list):
    env_list = get_all_env()
    env = next((item for item in input_list if item in env_list), env_list[0])
    new_list = [item for item in input_list if item != env]
    return env, new_list
    
def find_and_remove_operator(input_list):
    operator = 'and'
    new_list = []
    for item in input_list:
        if item in ('or', 'and'):
            operator = item
        else:
            new_list.append(item)
    return operator, new_list
    
def find_and_remove_first_int(input_list):
    found_int = next((item for item in input_list if is_int(item)), 0)
    new_list = [item for item in input_list if item != found_int]
    return found_int, new_list

def parse_args_message(arg1, arg2, arg3='', arg4='', arg5='', arg6='', arg7='', message_type=RunOperationMessage):
    global HELP, DEBUG, EDIT
    key = arg1
    params = [arg for arg in [arg2, arg3, arg4, arg5, arg6, arg7] if arg]
    HELP, params = find_and_remove_flag(params, '-help')
    DEBUG, params = find_and_remove_flag(params, '-debug')
    EDIT, params = find_and_remove_flag(params, '-edit')
    count, params = find_and_remove_first_int(params)
    command, params = find_and_remove_command(params)
    env, params = find_and_remove_env(params)
    operator = None
    if message_type == RunUrlMessage:
        operator, params = find_and_remove_operator(params)
    debug(f'parameters: {params}')
    switch_1 = params[0] if len(params) > 0 else ''
    switch_2 = params[1] if len(params) > 1 else ''
    switch_3 = params[2] if len(params) > 2 else ''
    if message_type == RunUrlMessage:
        return message_type(key, command, env, count, operator, switch_1, switch_2, switch_3)
    elif message_type == RunInfoMessage:
        return message_type(key, command, switch_1, switch_2, switch_3)
    return message_type(key, command, env, count, switch_1, switch_2, switch_3)

def run_command(arg1='', arg2='', arg3='', arg4='', arg5='', arg6='', arg7=''):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(current_dir, '..'))
    key_dir = os.path.join(current_dir, arg1)
    user_file_path = os.path.join(root_dir, 'user_configuration.json')
    url_file_path = os.path.join(key_dir, 'urls.json')
    info_file_path = os.path.join(key_dir, 'info.diff')
    info_link_file_path = os.path.join(key_dir, 'info.lnk')
    if os.path.exists(info_file_path):
        runMessage = parse_args_message(arg1, arg2, arg3, arg4, arg5, arg6, arg7, RunInfoMessage)
        run_info(runMessage, current_dir, key_dir, info_file_path, user_file_path)
    elif os.path.exists(info_link_file_path):
        runMessage = parse_args_message(arg1, arg2, arg3, arg4, arg5, arg6, arg7, RunInfoMessage)
        info_file_path = get_target_path(info_link_file_path)
        run_info(runMessage, current_dir, key_dir, info_file_path, user_file_path)
    elif os.path.exists(url_file_path):
        runMessage = parse_args_message(arg1, arg2, arg3, arg4, arg5, arg6, arg7, RunUrlMessage)
        run_url(runMessage, current_dir, key_dir, url_file_path, user_file_path)
    else:
        runMessage = parse_args_message(arg1, arg2, arg3, arg4, arg5, arg6, arg7, RunOperationMessage)
        run_operation(runMessage, current_dir, key_dir, user_file_path)


def run_info(runMessage, current_dir, key_dir, info_file_path, user_file_path):
    if HELP or EDIT:
        subprocess.Popen(['start', notepad_app_path, '-ldiff', info_file_path], shell=True)
    else:
        sys.path.append(current_dir)
        try:
            x_module = importlib.import_module('parse_info')
            x_module.main(runMessage, info_file_path, user_file_path)
        except ImportError as e:
            print(e)
            continue_terminal()
        finally:
            sys.path.remove(current_dir)

def run_url(runMessage, current_dir, key_dir, url_file_path, user_file_path):
    if HELP or EDIT:
        subprocess.Popen([json_edit_app_path, url_file_path])
    else:
        sys.path.append(current_dir)
        try:
            x_module = importlib.import_module('parse_urls')
            x_module.main(runMessage, url_file_path, user_file_path)
        except ImportError as e:
            print(e)
            continue_terminal()
        finally:
            sys.path.remove(current_dir)

def run_operation(runMessage, current_dir, key_dir, user_file_path):
    if runMessage.command is None:
        if HELP:
            print_all_commands_help(key_dir, runMessage.key)
            continue_terminal()
        else:
            runMessage.command = '_'
            continue_with_command(runMessage, current_dir, key_dir)
    else:
        continue_with_command(runMessage, current_dir, key_dir)

class LazyModule:
    def __init__(self, module_name):
        self.module_name = module_name
        self.module = None

    def __getattr__(self, item):
        if self.module is None:
            self.module = importlib.import_module(self.module_name)
        return getattr(self.module, item)

def continue_with_command(runMessage, current_dir, key_dir):
    script_command = f"{runMessage.command}.py"
    script_path = os.path.join(key_dir, script_command)
    if os.path.exists(script_path):
        sys.path.append(current_dir)
        try:
            module_name = f'{runMessage.key}.{runMessage.command}'
            x_module = LazyModule(module_name)
            switch_1_attr = getattr(x_module, runMessage.switch_1, None)
            if runMessage.switch_1 and switch_1_attr and callable(switch_1_attr):
                if HELP:
                    print(switch_1_attr.__doc__)
                    continue_terminal() 
                else:
                    switch_1_attr(to_sub_command_message(runMessage))
            else:
                main_attr = getattr(x_module, "main", None)
                if HELP:
                    print(main_attr.__doc__)
                    continue_terminal()
                else:
                    main_attr(to_main_command_message(runMessage))
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
    args = sys.argv[1:]
    if not args:
        print('key and command are needed, like:')
        print('o shot ...')
        print('u git ...')
    else:
        run_command(*args)

entry()