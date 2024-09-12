from message import (MainCommandMessage, SubCommandMessage, get_open_source_app_dir, get_download_dir)
import os
from pathlib import Path
import subprocess
from explorer_utils import get_selected_file_path

download_path = get_download_dir()
app_path = os.path.join(get_open_source_app_dir(), 'FirstObjectXmlEditor', 'foxe.exe')

def _get_n_recent_files(num):
    files = [file for file in Path(download_path).glob(f'*.xml') if file.is_file()]
    sorted_files = sorted(files, key=lambda x: os.path.getmtime(x), reverse=True)
    if not sorted_files:
        return None
    return sorted_files[:num]

def _get_n_recent_file(num):
    files = [file for file in Path(download_path).glob(f'*.xml') if file.is_file()]
    sorted_files = sorted(files, key=lambda x: os.path.getmtime(x), reverse=True)
    if not sorted_files:
        return None
    if 1 <= num <= len(sorted_files):
        return sorted_files[num - 1]
    else:
        return None


def main(message: MainCommandMessage):
    '''
Open csv file from default directory, num specify only the nth recent file to open
'''
    number = 1 if message.num == 0 else message.num
    file, _ = get_selected_file_path()
    if not file:
        file = _get_n_recent_file(int(number))

    if not file :
        subprocess.Popen([app_path])
    else:        
        subprocess.Popen([app_path, file ])

def all(message: SubCommandMessage):
    '''
Open n csv files from default directory, num specify all nth recent files to open
'''
    number = 1 if message.num == 0 else message.num
    files = _get_n_recent_files(int(number))
    if not files :
        subprocess.Popen([app_path ])
    else:
        for file in files:
            subprocess.Popen([app_path, file ])

def to(message: SubCommandMessage):
    '''
Convert xml message to another type
Example usage: xml to txt
'''
    if message.switch_1 == 'txt' or message.switch_1 == 'text':
        create_text_flag = True
        file, _ = get_selected_file_path()
        if not file:
            xml_content = input('Enter xml content: ')
            create_text_flag = False
        else:
            with open(file, 'r') as f:
                xml_content = f.read()
        txt_content = xml_content.replace('\n', '').replace('\r', '').replace('\t', '').replace('"', '\\"')
        if create_text_flag:
            with open(file.replace('.xml', '.txt'), 'w') as f:
                f.write(txt_content)
        else:
            print()
            print('Text content:')
            print()
            print(txt_content)
            print('')
            input('Press any key to exit ...')
            
        