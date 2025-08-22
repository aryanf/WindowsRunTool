from message import (MainCommandMessage, SubCommandMessage)
from aws_utils import get_aws_cred




def main(message: MainCommandMessage):
    '''
Copy AWS credentials to clipboard
'''
    if message.switch_1 and message.switch_1 not in ['admin', 'readonly', 'developer']:
        print(f"Invalid role: {message.switch_1}")
        return
    else:
        get_aws_cred(message.env, message.switch_1)