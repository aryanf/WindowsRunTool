from message import (MainCommandMessage, SubCommandMessage, get_open_source_app_dir)
import subprocess
import os

qdir_path = os.path.join(get_open_source_app_dir(), 'Q-Dir', 'Q-Dir_x64.exe')
app_dir_path = os.path.join(get_open_source_app_dir(), 'ShareX')
app_path = os.path.join(get_open_source_app_dir(), 'ShareX', 'ShareX.exe')
shot_dir_path = os.path.join(get_open_source_app_dir(), 'ShareX', 'ShareX', 'Screenshots')

def main(message: MainCommandMessage):
    '''
Take a screenshot
'''
    subprocess.Popen([app_path, '-RectangleRegion'])

def long(message: SubCommandMessage):
    '''
Take a long screenshot
'''
    print('long screenshot')
    subprocess.Popen([app_path, '-ScrollingCapture'])

def dir(message: SubCommandMessage):
    '''
Open the directory of the screenshot
'''
    subprocess.Popen([qdir_path, shot_dir_path, app_dir_path], shell=True)    
