from message import (MainCommandMessage, SubCommandMessage, get_open_source_app_dir)
import subprocess
import os


app_path = os.path.join(get_open_source_app_dir(), 'Everything', 'Everything.exe')

def main(message: MainCommandMessage):
    '''
Find a file using Everything
'''
    subprocess.Popen([app_path])