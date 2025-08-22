from message import (MainCommandMessage, SubCommandMessage, get_open_source_app_dir)
import subprocess
import os


username = os.getenv('USER') or os.getenv('LOGNAME') or os.getenv('USERNAME')
dbeaver_path = f'C:\\Users\\{username}\\AppData\\Local\\DBeaver\\dbeaver.exe'

def main(message: MainCommandMessage):
    '''
Open DBeaver
'''
    subprocess.Popen([dbeaver_path, '-nl', 'en'])