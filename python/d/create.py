from message import (MainCommandMessage)
from pyvda import VirtualDesktop


def main(message: MainCommandMessage):
    '''
Create a new virtual desktop
'''
    if message.switch_1:
        name = message.switch_1
    else:
        name = input('Enter new desktop name: ')
    new_desktop = VirtualDesktop.create()
    new_desktop.rename(name)
    VirtualDesktop.go(new_desktop)  