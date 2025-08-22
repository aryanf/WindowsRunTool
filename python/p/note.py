from message import (MainCommandMessage, SubCommandMessage, get_open_source_app_dir, get_document_dir)
import os
import shutil
import subprocess

document_path = get_document_dir()
app_path = os.path.join(get_open_source_app_dir(), 'Notepad++64', 'notepad++.exe')
template_path = os.path.join(get_open_source_app_dir(), 'Notepad++64', 'template.txt')


def main(message: MainCommandMessage):
    '''
Open notepad++ if not parameter is provided, or 
create a file in Document directory with foldable structure
{switch_1}: file name which is stored in default location
'''
    if(message.switch_1==''):
        subprocess.Popen(['start', app_path], shell=True)
    else:
        note_path = os.path.join(document_path, f'{message.switch_1}.diff')
        if not os.path.exists(note_path):
            shutil.copy2(template_path, note_path) 
        subprocess.Popen(['start', app_path, '-ldiff', note_path], shell=True)

def dir(message: SubCommandMessage):
    '''
Open the directory of the files
'''
    subprocess.Popen(['explorer', document_path], shell=True)

def new(message: SubCommandMessage):
    '''
Open notepad++ as new instance if not parameter is provided, or 
create a file in Document directory with foldable structure
{switch_1}: file name which is stored in default location
'''
    if(message.switch_1==''):
        subprocess.Popen(['start', app_path, '-multiInst'], shell=True)
    else:
        note_path = os.path.join(document_path, f'{message.switch_1}.diff')
        if not os.path.exists(note_path):
            shutil.copy2(template_path, note_path) 
        subprocess.Popen(['start', app_path, '-ldiff', note_path], shell=True)