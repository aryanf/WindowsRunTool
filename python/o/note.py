from message import (MainCommandMessage, SubCommandMessage, get_open_source_app_dir)
import os
import shutil
import subprocess


username = os.getenv('USER') or os.getenv('LOGNAME') or os.getenv('USERNAME')
document_path = f'C:\\Users\\{username}\\Documents\\'
app_path = os.path.join(get_open_source_app_dir(), 'Notepad++64', 'notepad++.exe')
template_path = os.path.join(get_open_source_app_dir(), 'Notepad++64', 'template.txt')


def main(message: MainCommandMessage):
    '''
Open notepad++ if not parameter is provided, or 
create a file in Document directory with foldable structure
{switch_1}: file name which is stored in default location
'''
    if(message.switch_1==''):
        subprocess.Popen([app_path])
    else:
        note_path = os.path.join(document_path, f'{message.switch_1}.txt')
        if not os.path.exists(note_path):
            shutil.copy2(template_path, note_path) 
        subprocess.Popen(['start', app_path, '-ldiff', note_path], shell=True)

