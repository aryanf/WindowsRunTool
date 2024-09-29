from message import (MainCommandMessage, SubCommandMessage)
from window_utils import get_selected_files_path_in_top_file_explorer
import time
import zipfile
import os

def main(message: MainCommandMessage):
    '''
Zip selected file or folder in top file explorer
'''
    source, _ = get_selected_files_path_in_top_file_explorer()
    if not source:
        print('No file or folder selected')
        time.sleep(2)
        return
    print(f'Zipping {len(source)} files/folders...')
    # Determine the zip file name based on the source name
    if len(source)==1 and os.path.isdir(source[0]):
        zip_name = os.path.basename(source[0].rstrip('/')) + '.zip'
    else:
        zip_name = os.path.splitext(os.path.basename(source[0]))[0] + '.zip'
    destination = os.path.join(os.path.dirname(source[0]), zip_name)
    print(destination)
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Check if the source is a file
            if len(source)==1 and os.path.isfile(source[0]):
                zipf.write(source[0], os.path.basename(source[0]))
            # If the source is a directory
            elif len(source)==1 and os.path.isdir(source[0]):
                # Walk the directory
                for root, dirs, files in os.walk(source[0]):
                    for file in files:
                        # Create the full path
                        file_path = os.path.join(root, file)
                        # Add file to the zip, preserving folder structure
                        zipf.write(file_path, os.path.relpath(file_path, source[0]))
            elif len(source)>1:
                for item in source:
                    if os.path.isfile(item):
                        zipf.write(item, os.path.basename(item))
                    elif os.path.isdir(item):
                        _add_folder_to_zip(zipf, item)
            else:
                print(f"The specified source '{source}' is neither a file nor a folder.")


def _add_folder_to_zip(zipf, folder_path):
    for root, dirs, files in os.walk(folder_path):
        # Add the directory itself to the zip file
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            zipf.write(dir_path, os.path.relpath(dir_path, os.path.dirname(folder_path)) + '/')
        
        # Add the files in the directory to the zip file
        for file in files:
            file_path = os.path.join(root, file)
            zipf.write(file_path, os.path.relpath(file_path, os.path.dirname(folder_path)))
