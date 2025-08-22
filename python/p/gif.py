from message import (MainCommandMessage, SubCommandMessage, get_open_source_app_dir)
import subprocess
import os

qdir_path = os.path.join(get_open_source_app_dir(), 'Q-Dir', 'Q-Dir_x64.exe')
app_dir_path = os.path.join(get_open_source_app_dir(), 'ShareX')
app_path = os.path.join(get_open_source_app_dir(), 'ShareX', 'ShareX.exe')
shot_dir_path = os.path.join(get_open_source_app_dir(), 'ShareX', 'ShareX', 'Screenshots')

def main(message: MainCommandMessage):
    '''
Record a gif
'''
    subprocess.Popen([app_path, '-ScreenRecorderGif'])

def dir(message: SubCommandMessage):
    '''
Open the directory of the gif
'''
    subprocess.Popen([qdir_path, shot_dir_path, app_dir_path], shell=True)