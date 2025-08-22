from message import (MainCommandMessage, SubCommandMessage, get_open_source_app_dir)
import subprocess
import os

username = os.getenv('USER') or os.getenv('LOGNAME') or os.getenv('USERNAME')
postman_path = f'C:\\Users\\{username}\\AppData\\Local\\Postman\\Postman.exe'
nodejs_path = f'C:\\Users\\{username}\\app.js'

'''
Nodejs script to run
install npm from https://nodejs.org/en/download/
npm install express body-parser
create app.js in user (aryan.firouzian) directory with content
run: node app.js
'''

def main(message: MainCommandMessage):
    '''
Run postman and nodejs server to communicate with postman
'''
    try:
        subprocess.Popen([postman_path])
        process = subprocess.Popen(['node', nodejs_path], shell=True)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            print(f"Error: {stderr.decode('utf-8')}")
        else:
            print(f"Output: {stdout.decode('utf-8')}")
    except Exception as e:
        print(f'Error: {e}')
        input('Press any key to continue...')

