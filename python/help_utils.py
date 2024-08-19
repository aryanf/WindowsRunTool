import os
import ast
import shutil
import win32gui
import win32con
import curses_terminal
import importlib

hwnd = win32gui.GetForegroundWindow()
win32gui.SetWindowPos(hwnd,win32con.HWND_TOP,1,1,900,800,0)

def convert_nested_dict(d):
    result = {}
    for key, value in d.items():
        if isinstance(value, dict):
            result[key] = convert_nested_dict(value)
        else:
            result[key] = value
    return result

def display_strings_in_columns(all_module_functions, all_functions_per_module, terminal_width):
    max_length = max(len(s) for s in all_module_functions) + 15
    num_columns = terminal_width // max_length
    num_rows = max(-(-len(all_module_functions) // num_columns), 10)

    for i in range(num_rows):
        for j in range(num_columns):
            index = i + j * num_rows
            if index < len(all_module_functions):
                if i==0:
                    print(f"{all_module_functions[index]:<{max_length}}", end="\t")
                else:
                    print(f"{all_functions_per_module[index]:<{max_length}}", end="\t")
        print()

def extract_functions(file_path):
    functions = []
    with open(file_path, 'r') as file:
        tree = ast.parse(file.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                functions.append(node.name)
    sorted_functions = sorted(functions, key=lambda x: x != "main")
    return sorted_functions

def get_terminal_width():
    try:
        columns, _ = shutil.get_terminal_size()
        return columns
    except:
        return 80  # Default value if terminal size cannot be determined

def print_functions_in_directory(key_dir, key):
    temp_module_names = []
    all_module_functions = []
    all_functions_per_module = []
    for filename in os.listdir(key_dir):
        if filename.endswith('.py'):
            file_path = os.path.join(key_dir, filename)
            functions = extract_functions(file_path)
            counter = 0
            for function in functions:
                module_name = os.path.splitext(filename)[0]
                temp_module_names.append(module_name)
            longest_length = len(max(temp_module_names, key=len))
            for function in functions:
                temp_module_name = os.path.splitext(filename)[0]
                module_name = temp_module_name + ' '*(longest_length-len(temp_module_name))
                masked_function_name = function if function!='main' else (' ' if len(functions)==1 else '')
                all_module_functions.append(f'{temp_module_name} {masked_function_name}')
                masked_module_name = module_name if counter == 0 else len(module_name)*" "
                all_functions_per_module.append(f'{masked_module_name} {masked_function_name}')
                counter = counter + 1
    
    display(all_module_functions, all_functions_per_module, key, key_dir)

def display(all_module_functions, all_functions_per_module, key, key_dir, default_selected_index=0):
    i, cmd = curses_terminal.show(all_module_functions, enumerating=False, zero_indexed=False, info='', item_per_col=30, default_selected_index=default_selected_index)
    print(i)
    if cmd in all_module_functions:
        params = cmd.strip().split(' ')
        script_command = f"{params[0]}.py"
        script_path = os.path.join(key_dir, script_command)
        x_module = importlib.import_module(f'{key}.{params[0]}')
        os.system('cls')    
        if len(params) > 1:
            print(getattr(x_module, params[1]).__doc__)
        else:
            print(getattr(x_module, 'main').__doc__)
        print('Press the "Enter" key ...')
        input()
        os.system('cls')    
        display(all_module_functions, all_functions_per_module, key, key_dir)
    elif cmd == 'q' or cmd == 'quit' or cmd == 'exit' or cmd == 'e':
        exit()
    else:
        print_all_commands_help(key_dir, key)
    
def print_all_commands_help(key_dir, key):
    print_functions_in_directory(key_dir, key)