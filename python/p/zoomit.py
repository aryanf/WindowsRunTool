from message import (MainCommandMessage, SubCommandMessage, get_open_source_app_dir)
import subprocess
import os
import time

app_path = os.path.join(get_open_source_app_dir(), 'ZoomIt', 'ZoomIt.exe')

def main(message: MainCommandMessage):
    '''
Open ZoomIt
'''
    print('zoomit')
    print('use Ctrl+1 to zoom in, Ctrl+2 to draw.')
    subprocess.Popen([app_path])
