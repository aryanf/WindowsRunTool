from message import (MainCommandMessage, SubCommandMessage, get_open_source_app_dir)
from aws_utils import _get_cached_cred
import time
import pyperclip
import chrome_utils
from windows_toasts import Toast, WindowsToaster
from windows_toasts.wrappers import ToastDuration


timer_list_title_mouse_dic = { 'timer': 20, 'title_mouse': [
    { 'title': 'Sign in to your account', 'mouse': (1119, 652) },
    { 'title': 'Amazon Web Services (AWS)', 'mouse': (973, 850) },
    { 'title': 'AWS access portal', 'mouse': (1257, 777) }
    ] 
} 

def main(message: MainCommandMessage):
    '''
Copy AWS credentials to clipboard as bash variables
'''
    chrome_utils.auto_chrome(timer_list_title_mouse_dic)
    success, access_key_id, secret_access_key, session_token = _get_cached_cred(message.env, message.switch_1)
    if success:
        region = 'export AWS_DEFAULT_REGION=eu-west-1'
        pyperclip.copy(region)
        time.sleep(0.5)
        aws_cred = f"""export AWS_ACCESS_KEY_ID="{access_key_id}"
export AWS_SECRET_ACCESS_KEY="{secret_access_key}"
export AWS_SESSION_TOKEN="{session_token}" """
        pyperclip.copy(aws_cred)
        _complete_toast()

def csharp(message: SubCommandMessage):
    '''
Copy AWS credentials to clipboard as csharp variable
'''
    chrome_utils.auto_chrome(timer_list_title_mouse_dic)
    success, access_key_id, secret_access_key, session_token = _get_cached_cred(message.env, message.switch_1)
    if success:
        region = 'Environment.SetEnvironmentVariable("AWS_REGION", "eu-west-1");'
        pyperclip.copy(region)
        time.sleep(0.5)
        aws_cred = f"""Environment.SetEnvironmentVariable("AWS_ACCESS_KEY_ID", "{access_key_id}");
Environment.SetEnvironmentVariable("AWS_SECRET_ACCESS_KEY", "{secret_access_key}");
Environment.SetEnvironmentVariable("AWS_SESSION_TOKEN", "{session_token}");"""
        pyperclip.copy(aws_cred)
        _complete_toast()

def python(message: SubCommandMessage):
    '''
Copy AWS credentials to clipboard as python variable
'''
    chrome_utils.auto_chrome(timer_list_title_mouse_dic)
    success, access_key_id, secret_access_key, session_token = _get_cached_cred(message.env, message.switch_1)
    if success:
        region = "os.environ['AWS_DEFAULT_REGION'] = 'eu-west-1'"
        pyperclip.copy(region)
        time.sleep(0.5)
        aws_cred = f"""os.environ['AWS_ACCESS_KEY_ID'] = '{access_key_id}'
os.environ['AWS_SECRET_ACCESS_KEY'] = '{secret_access_key}'
os.environ['AWS_SESSION_TOKEN'] = '{session_token}' """
        pyperclip.copy(aws_cred)
        _complete_toast()

def vscode(message: SubCommandMessage):
    '''
Copy AWS credentials to clipboard as python variable
'''
    chrome_utils.auto_chrome(timer_list_title_mouse_dic)
    success, access_key_id, secret_access_key, session_token = _get_cached_cred(message.env, message.switch_1)
    if success:
        region = '"AWS_DEFAULT_REGION":"eu-west-1"'
        pyperclip.copy(region)
        time.sleep(0.5)
        aws_cred = f'''"AWS_ACCESS_KEY_ID":"{access_key_id}",
"AWS_SECRET_ACCESS_KEY":"{secret_access_key}",
"AWS_SESSION_TOKEN":"{session_token}"'''
        pyperclip.copy(aws_cred)
        _complete_toast()

def env(message: SubCommandMessage):
    '''
Copy AWS credentials to clipboard as env variable list file
'''
    chrome_utils.auto_chrome(timer_list_title_mouse_dic)
    success, access_key_id, secret_access_key, session_token = _get_cached_cred(message.env, message.switch_1)
    if success:
        region = 'AWS_DEFAULT_REGION=eu-west-1'
        pyperclip.copy(region)
        time.sleep(0.5)
        aws_cred = f'''AWS_ACCESS_KEY_ID={access_key_id}
AWS_SECRET_ACCESS_KEY={secret_access_key}
AWS_SESSION_TOKEN={session_token}'''
        pyperclip.copy(aws_cred)
        _complete_toast()

def cmd(message: SubCommandMessage):
    '''
Copy AWS credentials to clipboard as Windows CMD set commands
'''
    chrome_utils.auto_chrome(timer_list_title_mouse_dic)
    success, access_key_id, secret_access_key, session_token = _get_cached_cred(message.env, message.switch_1)
    if success:
        region = 'set AWS_DEFAULT_REGION=eu-west-1'
        pyperclip.copy(region)
        time.sleep(0.5)
        aws_cred = f'''set AWS_ACCESS_KEY_ID={access_key_id}
set AWS_SECRET_ACCESS_KEY={secret_access_key}
set AWS_SESSION_TOKEN={session_token}'''
        pyperclip.copy(aws_cred)
        _complete_toast()

def _complete_toast():
    toaster = WindowsToaster('AWS Credentials')
    newToast = Toast(['in clipboard'], duration=ToastDuration.Short)
    toaster.show_toast(newToast)