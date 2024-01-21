from message import (MainCommandMessage, SubCommandMessage, get_open_source_app_dir)
import subprocess
import os


app_path = os.path.join(get_open_source_app_dir(), 'WinMerge', 'WinMergeU.exe')

def main(message: MainCommandMessage):
    '''
Open WinMerge to compare text strings, files or directories
'''
    subprocess.Popen([app_path, '-new'])
