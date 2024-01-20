from message import (MainCommandMessage, SubCommandMessage, get_open_source_app_dir)
import subprocess
import os


app_path = os.path.join(get_open_source_app_dir(), 'ScreenToGif', 'ScreenToGif.exe')

def main(message: MainCommandMessage):
    '''
Crop image of snipping tool, it is copied to clipboard
'''
    subprocess.Popen([app_path, '-n', '-o', 's', '-r', '7,30,1520,770', '-f', '15fps', '-c'])




