from message import (MainCommandMessage, SubCommandMessage)
from explorer_utils import get_selected_file_path
import time
import zipfile
import os

def main(message: MainCommandMessage):
    '''
Zip selected file or folder in top file explorer
'''
    source = get_selected_file_path()
    if not source:
        print('No file or folder selected')
        time.sleep(2)
        return
    print(f'Zipping {source}')
    # Determine the zip file name based on the source name
    if os.path.isdir(source):
        zip_name = os.path.basename(source.rstrip('/')) + '.zip'
    else:
        zip_name = os.path.splitext(os.path.basename(source))[0] + '.zip'
    destination = os.path.join(os.path.dirname(source), zip_name)
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Check if the source is a file
            if os.path.isfile(source):
                zipf.write(source, os.path.basename(source))
            # If the source is a directory
            elif os.path.isdir(source):
                # Walk the directory
                for root, dirs, files in os.walk(source):
                    for file in files:
                        # Create the full path
                        file_path = os.path.join(root, file)
                        # Add file to the zip, preserving folder structure
                        zipf.write(file_path, os.path.relpath(file_path, source))
            else:
                print(f"The specified source '{source}' is neither a file nor a folder.")
