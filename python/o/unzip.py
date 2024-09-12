from message import (MainCommandMessage, SubCommandMessage)
from explorer_utils import get_selected_file_path
import time
import zipfile
import os

def main(message: MainCommandMessage):
    '''
Zip selected file or folder in top file explorer
'''
    zip_path, _ = get_selected_file_path()
    if not zip_path:
        print('No file or folder selected')
        time.sleep(2)
        return
    if not zipfile.is_zipfile(zip_path):
        print(f"The specified file '{zip_path}' is not a valid zip file.")
        return
    print(f'Unzipping {zip_path}')

    # Create the output directory based on the zip file name
    output_dir = os.path.splitext(zip_path)[0]
    
    # Extract all the contents of the zip file into the output directory
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(output_dir)
    
    print(f"Unzipped to '{output_dir}'")
