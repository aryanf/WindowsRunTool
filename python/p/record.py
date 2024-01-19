from message import (MainCommandMessage, SubCommandMessage)

def main(message: MainCommandMessage):
    '''
Recording a video. You should stop the video
'''
    print('video recording ...')

def short(message: SubCommandMessage):
    '''
Recording a 15 min video
'''
    print('recording a short video')