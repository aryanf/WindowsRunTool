#dev
#6f462b
from message import (MainCommandMessage, SubCommandMessage)
import requests
import time
import uuid
from windows_toasts import Toast, WindowsToaster
from windows_toasts.wrappers import ToastDuration

def main(message: MainCommandMessage):
    '''
    Main function for case command
    Set a case id that can be used by postman or other tools

'''
    case_id = message.switch_1
    print(case_id)
    # Generate UUID using uuid4 (random UUID)
    case_uuid = uuid.uuid4()
    print(str(case_uuid))
    # Decimal form of the UUID is always 39 digits after padding, so 18 digits are guaranteed
    case_18digits = str(case_uuid.int).zfill(39)[:18]
    print(case_18digits)
    _post_case_id_to_storage(case_id=case_id, case_uuid=str(case_uuid), case_18digits=case_18digits)


def _post_case_id_to_storage(case_id, case_uuid, case_18digits):
    url = 'http://localhost:3000/set-clipboard-case-id'
    content_data = {
        "case_id": case_id,
        "case_uuid": case_uuid,
        "case_18digits": case_18digits,
    }
    try:
        response = requests.post(url, json=content_data)
        if response.status_code == 200:
            _complete_toast(f"Stored case id: {case_id}")
        else:
            print(f"Failed to store. Status not success.")
            time.sleep(2)
    except:
        print(f"Failed to post.")
        time.sleep(2)
    return

def _complete_toast(message):
    try:
        toaster = WindowsToaster('Token')
        newToast = Toast([message], duration=ToastDuration.Short)
        toaster.show_toast(newToast)
    except Exception as e:
        # Silently handle toast notification errors
        pass