from message import (MainCommandMessage, SubCommandMessage, get_open_source_app_dir)
from datetime import datetime
import os
import pyperclip
import time
import curses_terminal

username = os.getenv('USER') or os.getenv('LOGNAME') or os.getenv('USERNAME')

def main(message: MainCommandMessage):
    '''
    branch_type = message.switch_1
    ip_code = message.switch_2
    branch_desc = message.switch_3
    '''
    try:
        branch_type = ''
        ip_code = ''
        branch_desc = ''
        if message.switch_1:
            branch_type = message.switch_1
        else:
            _, branch_type = curses_terminal.show(options=['feature', 'fix', 'hotfix', 'chore', 'refactor', 'test', 'doc', 'ci'],
                                                  info='Select branch type:', default_selected_index=0)
        if message.switch_2:
            ip_code = message.switch_2
        else:
            ip_code = input("Input ip_code (jira id):") 
        if message.switch_3:
            branch_desc = message.switch_3
        else:
            branch_desc = input("Input branch description:")

        current_date = datetime.now()
        formatted_date = current_date.strftime("%Y%m%d")
        if ip_code:
            new_branch = f'{branch_type}/{username.lower()}/{formatted_date}/{ip_code}_{branch_desc}'
        else:
            new_branch = f'{branch_type}/{username.lower()}/{formatted_date}/{branch_desc}'
        pyperclip.copy(new_branch)
        time.sleep(0.5)
        git_push_command = f'git push --set-upstream origin {new_branch} '
        pyperclip.copy(git_push_command)
        time.sleep(0.5)
        git_commands = f'git checkout -b {new_branch}'
        pyperclip.copy(git_commands)
        _confirmed_copy()
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(10)

def _confirmed_copy():
    print("commands copied")
    time.sleep(0.5)