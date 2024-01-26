from message import (MainCommandMessage, SubCommandMessage, get_open_source_app_dir)
import subprocess
import os


app_path = os.path.join(get_open_source_app_dir(), 'Frhed', 'frhed.exe')

def main(message: MainCommandMessage):
    '''
Binary editor with hex conversion
'''
    subprocess.Popen([app_path])