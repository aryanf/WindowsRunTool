from message import (MainCommandMessage, SubCommandMessage)
import subprocess

chrome_path = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'

def main(message: MainCommandMessage):
    '''
Run syncthing on wsl
'''
    print('run syncthing on wsl')
    subprocess.Popen(['wsl', 'syncthing', 'serve', '--no-browser', '--logflags=0'])

def open(message:SubCommandMessage):
    '''
Open syncthing web UI
'''
    print('open syncthing web UI')
    subprocess.Popen([chrome_path, 'http://127.0.0.1:8384'])