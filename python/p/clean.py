from message import (MainCommandMessage, SubCommandMessage)
import os
from windows_toasts import Toast, WindowsToaster
from windows_toasts.wrappers import ToastDuration

username = os.getenv('USER') or os.getenv('LOGNAME') or os.getenv('USERNAME')
known_host_path = f'C:\\Users\\{username}\\.ssh\\known_hosts'


def host(message:SubCommandMessage):
    '''
    Clean all rows with bastion pattern in host file
    '''
    pattern = 'bastion'
    print('cleaning host file ...')
    with open(known_host_path, "r") as f:
        lines = f.readlines()
    with open(known_host_path, "w") as f:
        for line in lines:
            if not line.startswith(pattern):
                f.write(line)
    _complete_toast('cleaned')

def _complete_toast(message):
    toaster = WindowsToaster('Host File')
    newToast = Toast([message], duration=ToastDuration.Short)
    toaster.show_toast(newToast)