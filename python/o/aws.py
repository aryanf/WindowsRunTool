from message import (MainCommandMessage, SubCommandMessage, get_open_source_app_dir)
from aws_utils import get_aws_cred
import time
import pyperclip
import subprocess
from datetime import datetime
import pytz
import json


def main(message: MainCommandMessage):
    '''
Copy AWS credentials to clipboard
'''
    get_aws_cred(message.env)