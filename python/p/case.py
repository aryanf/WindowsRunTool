#dev
#6f462b
from message import (MainCommandMessage, SubCommandMessage)
import requests
import time

def main(message: MainCommandMessage):
    '''
    Main function for case command
    Set a case id that can be used by postman or other tools

'''
    case_id = message.switch_1
    print(case_id)
    _post_case_id_to_storage(case_id=case_id)


def _post_case_id_to_storage(case_id):
    url = 'http://localhost:3000/set-clipboard-case-id'
    content_data = {
        "case_id": case_id,
    }
    try:
        response = requests.post(url, json=content_data)
        if response.status_code == 200:
            print("Case stored")
            time.sleep(1)
        else:
            print(f"Failed to store. Status not success.")
            time.sleep(2)
    except:
        print(f"Failed to post.")
        time.sleep(2)
    return