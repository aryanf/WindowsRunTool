import os
import ast
import shutil

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

def print_functions_in_directory(directory):
    temp_module_names = []
    all_module_functions = []
    all_functions_per_module = []
    for filename in os.listdir(directory):
        if filename.endswith('.py'):
            file_path = os.path.join(directory, filename)
            functions = extract_functions(file_path)
            counter = 0
            for function in functions:
                module_name = os.path.splitext(filename)[0]
                temp_module_names.append(module_name)
            longest_length = len(max(temp_module_names, key=len))
            for function in functions:
                temp_module_name = os.path.splitext(filename)[0]
                module_name = temp_module_name + ' '*(longest_length-len(temp_module_name))
                masked_function_name = function if function!='main' else (' ' if len(functions)==1 else '.')
                all_module_functions.append(f'{module_name} {masked_function_name}')
                masked_module_name = module_name if counter == 0 else len(module_name)*" "
                all_functions_per_module.append(f'{masked_module_name} {masked_function_name}')
                counter = counter + 1
    terminal_width = get_terminal_width()
    display_strings_in_columns(all_module_functions, all_functions_per_module, terminal_width)

def print_all_commands_help(key_dir):
    print_functions_in_directory(key_dir)