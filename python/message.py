
class RunMessage:
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
    

def to_main_command_message(message: RunMessage)-> MainCommandMessage:
    return MainCommandMessage(message.env, message.num, message.switch_1, message.switch_2, message.switch_3)

def to_sub_command_message(message: RunMessage)-> SubCommandMessage:
    return SubCommandMessage(message.env, message.num, message.switch_2, message.switch_3)