from message import (MainCommandMessage, SubCommandMessage)
from window_utils import get_selected_files_path_in_top_file_explorer
import time
import zipfile
import tarfile
import py7zr
import rarfile
import os
import curses_terminal

def main(message: MainCommandMessage):
    '''
Zip selected file or folder in top file explorer
'''
    files, _ = get_selected_files_path_in_top_file_explorer()
    file_path = files[0] if files else None
    if not file_path:
        print('No file or folder selected')
        time.sleep(2)
        return
    # Create the output directory based on the zip file name
    extract_dir = os.path.splitext(file_path)[0]
    if zipfile.is_zipfile(file_path):
        _extract_zip(file_path, extract_dir)
    elif tarfile.is_tarfile(file_path):
        _extract_tar(file_path, extract_dir)
    elif file_path.endswith(".rar"):
        try:
            _extract_rar(file_path, extract_dir)
        except rarfile.BadRarFile:
            print("Failed to extract rar file")
    elif file_path.endswith(".7z"):
        try:
            _extract_7z(file_path, extract_dir)
        except py7zr.Bad7zFile:
            print("Failed to extract 7z file")
    else:
        print("Unsupported archive format")
    delete_confirmation = ['yes', 'no']
    i, _ = curses_terminal.show(delete_confirmation, enumerating=True, zero_indexed=True, info='Delete zip file?')
    if i == 0:
        os.remove(file_path)
    


def _extract_zip(file_path, extract_dir):
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

def _extract_tar(file_path, extract_dir):
    with tarfile.open(file_path, 'r:*') as tar_ref:
        tar_ref.extractall(extract_dir)

def _extract_rar(file_path, extract_dir):
    with rarfile.RarFile(file_path) as rar_ref:
        rar_ref.extractall(extract_dir)

def _extract_7z(file_path, extract_dir):
    with py7zr.SevenZipFile(file_path, mode='r') as z_ref:
        z_ref.extractall(extract_dir)