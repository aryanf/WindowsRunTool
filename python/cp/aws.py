from message import (MainCommandMessage, SubCommandMessage, get_open_source_app_dir)
from aws_utils import get_aws_cred, _get_cached_cred
import time
import pyperclip
import subprocess
from datetime import datetime
import pytz
import json


def main(message: MainCommandMessage):
    '''
Copy AWS credentials to clipboard as bash variables
'''
    success, access_key_id, secret_access_key, session_token = _get_cached_cred(message.env)
    if success:
        region = 'export AWS_DEFAULT_REGION=eu-west-1'
        pyperclip.copy(region)
        time.sleep(0.5)
        aws_cred = f"""export AWS_ACCESS_KEY_ID="{access_key_id}"
export AWS_SECRET_ACCESS_KEY="{secret_access_key}"
export AWS_SESSION_TOKEN="{session_token}" """
        pyperclip.copy(aws_cred)
        print(f"credentials copied")            
        time.sleep(1)


def csharp(message: SubCommandMessage):
    '''
Copy AWS credentials to clipboard as csharp variable
'''
    success, access_key_id, secret_access_key, session_token = _get_cached_cred(message.env)
    if success:
        region = 'Environment.SetEnvironmentVariable("AWS_REGION", "eu-west-1");'
        pyperclip.copy(region)
        time.sleep(0.5)
        aws_cred = f"""Environment.SetEnvironmentVariable("AWS_ACCESS_KEY_ID", "{access_key_id}");
Environment.SetEnvironmentVariable("AWS_SECRET_ACCESS_KEY", "{secret_access_key}");
Environment.SetEnvironmentVariable("AWS_SESSION_TOKEN", "{session_token}");"""
        pyperclip.copy(aws_cred)
        print(f"credentials copied")            
        time.sleep(1)

def python(message: SubCommandMessage):
    '''
Copy AWS credentials to clipboard as python variable
'''
    success, access_key_id, secret_access_key, session_token = _get_cached_cred(message.env)
    if success:
        region = "os.environ['AWS_DEFAULT_REGION'] = 'eu-west-1'"
        pyperclip.copy(region)
        time.sleep(0.5)
        aws_cred = f"""os.environ['AWS_ACCESS_KEY_ID'] = '{access_key_id}'
os.environ['AWS_SECRET_ACCESS_KEY'] = '{secret_access_key}'
os.environ['AWS_SESSION_TOKEN'] = '{session_token}' """
        pyperclip.copy(aws_cred)
        print(f"credentials copied")            
        time.sleep(1)

def vscode(message: SubCommandMessage):
    '''
Copy AWS credentials to clipboard as python variable
'''
    success, access_key_id, secret_access_key, session_token = _get_cached_cred(message.env)
    if success:
        region = '"AWS_DEFAULT_REGION":"eu-west-1"'
        pyperclip.copy(region)
        time.sleep(0.5)
        aws_cred = f'''"AWS_ACCESS_KEY_ID":"{access_key_id}",
"AWS_SECRET_ACCESS_KEY":"{secret_access_key}",
"AWS_SESSION_TOKEN":"{session_token}"'''
        pyperclip.copy(aws_cred)
        print(f"credentials copied")            
        time.sleep(1)
