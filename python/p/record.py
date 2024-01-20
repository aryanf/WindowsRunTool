from message import (MainCommandMessage, SubCommandMessage, get_open_source_app_dir)
import os
from datetime import datetime
import subprocess

username = os.getenv('USER') or os.getenv('LOGNAME') or os.getenv('USERNAME')
video_store_path = f'C:\\Users\\{username}\\Videos\\Captura'
if not os.path.exists(video_store_path):
    os.makedirs(video_store_path)
captura_cli_path = os.path.join(get_open_source_app_dir(), 'Captura', 'captura-cli.exe')

def main(message: MainCommandMessage):
    '''
Recording a video. You should stop the video
'''
    seconds = 7200 # 2hours
    if int(message.num) != 1:
        seconds = int(message.num) * 60
    name = message.switch_1 if message.switch_1 != '' else datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    file_path = os.path.join(video_store_path, f'{name}.avi')
    process = subprocess.Popen([captura_cli_path , 'list'], shell=True , stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return_code = process.wait()
    output, error = process.communicate()
    bluetooth = True if b'Jabra' in output else False
    subprocess.Popen([captura_cli_path, 'start', '--encoder', 'ffmpeg:1', '--length', str(seconds), f'--speaker={"2" if bluetooth else "0"}', '--mic=0', '--file', file_path])

def short(message: SubCommandMessage):
    '''
Recording a 15 min video
'''
    print('recording a short video')