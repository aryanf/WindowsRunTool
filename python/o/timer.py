from message import (MainCommandMessage, SubCommandMessage, get_open_source_app_dir)
import subprocess
import os


app_path = os.path.join(get_open_source_app_dir(), 'HourGlass', 'Hourglass.exe')

def main(message: MainCommandMessage):
    '''
Stopwatch 
{switch_1}: Unit time like d, day, days, h, hour, hours, m, min, minute, minutes, s, sec, second, seconds. Default is hour
{num}: Number of unit to count. Default is 1
'''
    # check https://alternativeto.net/software/hourglass-timer/about/ to modify command parameters
    units = ['d', 'day', 'days', 'h', 'hour', 'hours', 'm', 'min', 'minute', 'minutes', 's', 'sec', 'second', 'seconds']
    unit = message.switch_1 if message.switch_1 in units else 'hour'
    param = f'{message.num} {unit}'
    subprocess.Popen([app_path, '--loop-sound', 'on', param])