from message import (MainCommandMessage, get_root_project_dir)
import subprocess
import os


root_path = get_root_project_dir()
demo_path = app_directory = os.path.join(root_path, 'python', 'p', 'demo.py')
launch_path = app_directory = os.path.join(root_path, '.vscode', 'launch.json')

def main(message: MainCommandMessage):
    '''
Open WindowsRunTool in Visual Studio Code
'''
    subprocess.Popen(['start', 'code', root_path, launch_path, demo_path], shell=True)
