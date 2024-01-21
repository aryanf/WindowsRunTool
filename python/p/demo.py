from message import (MainCommandMessage, SubCommandMessage)

def main(message: MainCommandMessage):
    '''
Demo main function
This is an example to create more scripts and function
'''
    print('demo main function')
    message.print()
    input()


def func1(message:SubCommandMessage):
    '''
Demo main func1
This is an example to create more scripts and function
'''
    print('demo func1 function')
    message.print()
    input()


def func2(message:SubCommandMessage):
    '''
Demo main func2
This is an example to create more scripts and function
'''
    print('demo func2 function')
    message.print()
    input()