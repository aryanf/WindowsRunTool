from message import (MainCommandMessage, SubCommandMessage)
from aws_utils import get_aws_cred




def main(message: MainCommandMessage):
    '''
Copy AWS credentials to clipboard
'''
    get_aws_cred(message.env)