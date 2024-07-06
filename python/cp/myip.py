from message import (MainCommandMessage, SubCommandMessage, get_open_source_app_dir)
import pyperclip
import time
import requests

def main(message: MainCommandMessage):
    '''
Get my ip
    '''
    response = requests.get('https://ifconfig.me')
    if response.status_code == 200:
        myip = response.text.strip()
        pyperclip.copy(myip)
        print(myip)
        _confirmed_copy()
    else:
        print("Unable to retrieve IP address.")
        time.sleep(10)
    _confirmed_copy()


def _confirmed_copy():
    print("commands copied")
    time.sleep(0.5)