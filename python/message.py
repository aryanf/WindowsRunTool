import os
import json

class RunOperationMessage:
    def __init__(self, key, command, env, num, switch_1, switch_2, switch_3):    
        self.key = key
        self.command = command
        self.env = env
        self.num = num
        self.switch_1 = switch_1
        self.switch_2 = switch_2
        self.switch_3 = switch_3
    def print(self):
        print(f'key: {self.key}, command: {self.command}, env: {self.env}, num: {self.num}, switch1: {self.switch_1}, switch2: {self.switch_2}, switch3: {self.switch_3}')
    def to_string(self):
        return f'key: {self.key}, command: {self.command}, env: {self.env}, num: {self.num}, switch1: {self.switch_1}, switch2: {self.switch_2}, switch3: {self.switch_3}'

class RunUrlMessage:
    def __init__(self, key, command, env, num, operator, switch_1, switch_2, switch_3):    
        self.key = key
        self.command = command
        self.env = env
        self.num = 1 if num == 0 else num
        self.operator = operator
        self.switch_1 = switch_1
        self.switch_2 = switch_2
        self.switch_3 = switch_3
    def print(self):
        print(f'key: {self.key}, command: {self.command}, env: {self.env}, num: {self.num}, operator: {self.operator}, switch1: {self.switch_1}, switch2: {self.switch_2}, switch3: {self.switch_3}')
    def to_string(self):
        return f'key: {self.key}, command: {self.command}, env: {self.env}, num: {self.num}, operator: {self.operator}, switch1: {self.switch_1}, switch2: {self.switch_2}, switch3: {self.switch_3}'        

class RunInfoMessage:
    def __init__(self, key, command, switch_1, switch_2, switch_3):    
        self.key = key
        self.command = command
        self.switch_1 = switch_1
        self.switch_2 = switch_2
        self.switch_3 = switch_3
    def print(self):
        print(f'key: {self.key}, command: {self.command}, switch1: {self.switch_1}, switch2: {self.switch_2}, switch3: {self.switch_3}')
    def to_string(self):
        return f'key: {self.key}, command: {self.command}, switch1: {self.switch_1}, switch2: {self.switch_2}, switch3: {self.switch_3}'

class MainCommandMessage:
    def __init__(self, env, num, switch_1, switch_2, switch_3):
        self.env = env
        self.num = num
        self.switch_1 = switch_1
        self.switch_2 = switch_2
        self.switch_3 = switch_3
    def print(self):
        print(f'env: {self.env}, num: {self.num}, switch1: {self.switch_1}, switch2: {self.switch_2}, switch3: {self.switch_3}')
    def to_string(self):
        return f'env: {self.env}, num: {self.num}, switch1: {self.switch_1}, switch2: {self.switch_2}, switch3: {self.switch_3}'

class SubCommandMessage:
    def __init__(self, env, num, switch_1, switch_2):
        self.env = env
        self.num = num
        self.switch_1 = switch_1
        self.switch_2 = switch_2
    def print(self):
        print(f'env: {self.env}, num: {self.num}, switch1: {self.switch_1}, switch2: {self.switch_2}')
    def to_string(self):
        return f'env: {self.env}, num: {self.num}, switch1: {self.switch_1}, switch2: {self.switch_2}'

def to_main_command_message(message: RunOperationMessage)-> MainCommandMessage:
    return MainCommandMessage(message.env, message.num, message.switch_1, message.switch_2, message.switch_3)

def to_sub_command_message(message: RunOperationMessage)-> SubCommandMessage:
    return SubCommandMessage(message.env, message.num, message.switch_2, message.switch_3)

def get_open_source_app_dir():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_directory = os.path.dirname(current_dir)
    app_directory = os.path.join(root_directory, 'portable_open_source_apps')
    return app_directory

def get_root_project_dir():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_directory = os.path.dirname(current_dir)
    return root_directory

def get_user_configuration_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_directory = os.path.dirname(current_dir)
    user_configuration_path = os.path.join(root_directory, 'user_configuration.json')
    return user_configuration_path

def get_user_configuration():
    config = {}
    with open(get_user_configuration_path(), 'r') as file:
        config = json.load(file)
    return config

def get_all_env():
    return get_user_configuration().get('env', ['dev', 'staging', 'prod'])

def get_download_dir():
    return get_user_content_dir('Downloads')

def get_document_dir():
    return get_user_content_dir('Documents')

def get_video_dir():
    return get_user_content_dir('Videos')

def get_my_run_data_dir():
    return f'C:\\MyRunData\\'

def get_user_content_dir(content):
    download_path =  get_user_configuration()['paths'].get(content, '')
    if not os.path.exists(download_path):
        username = get_user_configuration().get('username', '')
        download_path = f'C:\\Users\\{username}\\{content}\\'
        if not os.path.exists(download_path):
            username = os.getenv('USER') or os.getenv('LOGNAME') or os.getenv('USERNAME')
            download_path = f'C:\\Users\\{username}\\{content}\\'
    return download_path

def get_user_name():
    config_username = get_user_configuration()['username']
    config_user_path = f'C:\\Users\\{config_username}\\'
    if not os.path.exists(config_user_path):
        found_username = os.getenv('USER') or os.getenv('LOGNAME') or os.getenv('USERNAME')
        found_user_path = f'C:\\Users\\{found_username}\\'
        found_user_path_lower = f'C:\\Users\\{found_username.lower()}\\'
        if os.path.exists(found_user_path):
            return found_username
        elif os.par.exists(found_user_path_lower):
            return found_username.lower()
        else:
            input(f'username cannot be set, modify user_configuration.json, and then continue ...')
    else:
        return config_username