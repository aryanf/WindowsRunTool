from message import (MainCommandMessage, SubCommandMessage, get_open_source_app_dir, get_document_dir)
import os
import shutil
import subprocess


document_path = get_document_dir()
app_path = os.path.join(get_open_source_app_dir(), 'Notepad++64', 'notepad++.exe')


def main(message: MainCommandMessage):
    '''
Open daily notepad++ 
'''
    daily_note_path = os.path.join(document_path, f'daily.diff')
    subprocess.Popen(['start', app_path, '-ldiff', daily_note_path], shell=True)

