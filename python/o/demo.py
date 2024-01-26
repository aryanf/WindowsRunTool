from message import (MainCommandMessage, SubCommandMessage)

def main(message: MainCommandMessage):
    '''
Demo main function
This is an example to create more scripts and function
'''
    print('demo main function')
    print(f'env: {message.env}, num: {message.num}, switch1: {message.switch_1}, switch2: {message.switch_2}, switch3: {message.switch_3}')
    input()


def func1(message:SubCommandMessage):
    '''
Demo main func1
This is an example to create more scripts and function
'''
    print('demo func1 function')
    print(f'env: {message.env}, num: {message.num}, switch1: {message.switch_1}, switch2: {message.switch_2}')
    input()


def func2(message:SubCommandMessage):
    '''
Demo main func2
This is an example to create more scripts and function
'''
    print('demo func2 function')
    print(f'env: {message.env}, num: {message.num}, switch1: {message.switch_1}, switch2: {message.switch_2}')
    input()