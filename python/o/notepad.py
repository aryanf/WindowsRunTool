from message import (MainCommandMessage, SubCommandMessage)
from o import note

def main(message: MainCommandMessage):
    '''
Open notepad++ if not parameter is provided, or 
create a file in Document directory with foldable structure
{switch_1}: file name which is stored in default location
'''
    note.main(message)

def dir(message: SubCommandMessage):
    '''
Open the directory of the files
'''
    note.dir(message)