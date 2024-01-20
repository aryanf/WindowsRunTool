import sys
import os
import time
from help_utils import(print_all_commands_help)
import importlib
from itertools import zip_longest
from message import (RunMessage, to_main_command_message, to_sub_command_message)

HELP = False
DEBUG = False
ENV_LIST = ['dev', 'staging', 'prod']  # First env item is the default


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
        if item == 'help':
            help_flag = True
        else:
            new_list.append(item)
    return help_flag, new_list

def find_and_remove_debug(input_list):
    debug_flag = False
    new_list = []
    for item in input_list:
        if item == 'debug':
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

def parse_args(arg1, arg2, arg3='', arg4='', arg5='', arg6='', arg7='') -> RunMessage:
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
    return RunMessage(key, command, env, count, switch_1, switch_2, switch_3)

def command(arg1='', arg2='', arg3='', arg4='', arg5='', arg6='', arg7=''):
    runMessage: RunMessage = parse_args(arg1, arg2, arg3, arg4, arg5, arg6, arg7)
    current_directory = os.path.dirname(os.path.abspath(__file__))
    directory_key = os.path.join(current_directory, runMessage.key)
    if runMessage.command == None:
        if HELP:
            print_all_commands_help(directory_key)
        else:
            print('Error: command should be provided ...')
    else:
        continue_with_command(runMessage, current_directory, directory_key)


def continue_with_command(runMessage: RunMessage, current_directory, directory_key):
    script_command = f"{runMessage.command}.py"
    script_path = os.path.join(directory_key, script_command)
    if os.path.exists(script_path):
        sys.path.append(current_directory)
        try:
            # Import the X module
            x_module = importlib.import_module(f'{runMessage.key}.{runMessage.command}')
            if (not runMessage.command.startswith('_') and 
                hasattr(x_module, runMessage.switch_1) and callable(getattr(x_module, runMessage.switch_1))):
                # Call the Z function
                if HELP:
                    print(getattr(x_module, runMessage.switch_1).__doc__)
                    input()
                else:
                    getattr(x_module, runMessage.switch_1)(to_sub_command_message(runMessage))
            else:
                if HELP:
                    print(getattr(x_module, "main").__doc__)
                    input()
                else:
                    getattr(x_module, "main")(to_main_command_message(runMessage))
        except ImportError as e:
            print(e)
            input()
        finally:
            # Remove the path to directory Y from the system path
            sys.path.remove(current_directory)
    else:
        print(f"Error: {script_path} not found in {directory_key}")
        input()



def entry():
    if len(sys.argv) == 1:
        print('key and command are needed, like:')
        print('p copy ...')
        print('l send ...')
    elif len(sys.argv) == 2:
        print('key and command are needed, like:')
        print(f'{sys.argv[1]} send ...')
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