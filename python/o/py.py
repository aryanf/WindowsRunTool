from message import (MainCommandMessage, get_root_project_dir)
import subprocess
import os


root_path = get_root_project_dir()
demo_path = app_directory = os.path.join(root_path, 'python', 'o', 'demo.py')

def main(message: MainCommandMessage):
    '''
Open WindowsRunTool in Visual Studio Code
'''
    subprocess.Popen(['start', 'code', root_path, demo_path], shell=True)
