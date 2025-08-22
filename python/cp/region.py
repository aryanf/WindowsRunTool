from message import (MainCommandMessage, SubCommandMessage, get_open_source_app_dir)
import pyperclip
import time

def main(message: MainCommandMessage):
    '''
Get aws region
    '''
    txt = 'export AWS_DEFAULT_REGION=eu-west-1'
    pyperclip.copy(txt)
    _confirmed_copy()


def _confirmed_copy():
    print("commands copied")
    time.sleep(0.5)