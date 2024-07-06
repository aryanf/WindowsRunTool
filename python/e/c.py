from message import (MainCommandMessage, SubCommandMessage, get_open_source_app_dir, get_document_dir)
import os
import shutil
import subprocess

app_path = os.path.join(get_open_source_app_dir(), 'Q-Dir', 'Q-Dir_x64.exe')
ina_fav_path = os.path.join(get_open_source_app_dir(), 'Q-Dir', 'Favoriten', 'all_c.qdr')

def main(message: MainCommandMessage):
    subprocess.Popen(['start', app_path, ina_fav_path], shell=True)