from message import (MainCommandMessage, SubCommandMessage, get_open_source_app_dir, get_document_dir)
import os
import shutil
import subprocess

app_path = os.path.join(get_open_source_app_dir(), 'Q-Dir', 'Q-Dir_x64.exe')

def main(message: MainCommandMessage):
    subprocess.run([app_path], shell=True)