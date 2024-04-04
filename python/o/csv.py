from message import (MainCommandMessage, SubCommandMessage, get_open_source_app_dir, get_download_dir)
import os
from pathlib import Path
import subprocess

download_path = get_download_dir()
app_path = os.path.join(get_open_source_app_dir(), 'CsvFileView', 'CSVFileView.exe')

def _get_n_recent_files(num):
    files = [file for file in Path(download_path).glob(f'*.csv') if file.is_file()]
    sorted_files = sorted(files, key=lambda x: os.path.getmtime(x), reverse=True)
    if not sorted_files:
        return None
    return sorted_files[:num]

def _get_n_recent_file(num):
    files = [file for file in Path(download_path).glob(f'*.csv') if file.is_file()]
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
    file = _get_n_recent_files(int(number))
    if not file :
        subprocess.Popen([app_path])
    else:        
        subprocess.Popen([app_path, file[0] ])

def all(message: SubCommandMessage):
    '''
Open n csv files from default directory, num specify all nth recent files to open
'''
    number = 1 if message.num == 0 else message.num
    files = _get_n_recent_file(int(number))
    if not files :
        subprocess.Popen([app_path ])
    else:
        for file in files:
            subprocess.Popen([app_path, file ])