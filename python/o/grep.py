from message import (MainCommandMessage, SubCommandMessage)
from message import (MainCommandMessage, get_open_source_app_dir)
import explorer_utils
import os
import subprocess

app_path = os.path.join(get_open_source_app_dir(), 'RipGrep', 'rg.exe')

def main(message: MainCommandMessage):
    '''
Search in files for a pattern
'''
    directory_path = explorer_utils.get_directory_path()
    subprocess.Popen([app_path, message.switch_1, directory_path])
    input()