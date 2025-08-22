from message import (MainCommandMessage, SubCommandMessage)
import pickle

def main(message: MainCommandMessage):
    '''
Show pkl data page by page
'''
    file_path = input('Enter the path to the pkl file: ')
    with open(file_path, "rb") as f:
        data = pickle.load(f)

    if isinstance(data, (list, tuple)):
        _paginate(data)
    elif isinstance(data, dict):
        _paginate(list(data.items()))
    else:
        print("Unsupported type:", type(data))

def _paginate(data, page_size=20):
    for i in range(0, len(data), page_size):
        input(f"\nShowing items {i} to {i + page_size - 1} (press Enter for more)...")
        chunk = data[i:i + page_size]
        for item in chunk:
            print(item)