import time
import pyperclip
import subprocess
from datetime import datetime
import pytz
import json


def get_aws_cred(env, role):
    success, access_key_id, secret_access_key, session_token = _get_cached_cred(env, role)
    if success:
        region = 'export AWS_DEFAULT_REGION=eu-west-1'
        pyperclip.copy(region)
        time.sleep(0.5)
        aws_cred = f"""export AWS_ACCESS_KEY_ID="{access_key_id}"
export AWS_SECRET_ACCESS_KEY="{secret_access_key}"
export AWS_SESSION_TOKEN="{session_token}" """
        pyperclip.copy(aws_cred)
        print(f"credentials copied")            
        time.sleep(1)


def _get_cached_cred(env, role):
    if not role:
        role = 'admin'
    if role not in ['admin', 'readonly', 'developer']:
        print(f"Invalid role: {role}")
        return False, '', '', ''
    profile = f'{env}-{role}'
    print(profile)
    aws_command = f"aws configure export-credentials --profile {profile}"
    try:
        aws_output = subprocess.check_output(aws_command, shell=True, stderr=subprocess.STDOUT)
        aws_output = aws_output.decode("utf-8")
        
        # Parse the JSON output
        credentials = json.loads(aws_output)

        # Access the credentials as needed
        access_key_id = credentials["AccessKeyId"]
        secret_access_key = credentials["SecretAccessKey"]
        session_token = credentials["SessionToken"]
        expiration = credentials["Expiration"]

        expiration_time = datetime.strptime(expiration, "%Y-%m-%dT%H:%M:%S%z")
        current_time = datetime.now(pytz.UTC)

        if current_time >= expiration_time:
            print("Expired")
            _refresh_credential(profile)
            return False, '', '', ''
        else:
            return True, access_key_id, secret_access_key, session_token

    except subprocess.CalledProcessError as e:
        print(f"Error running AWS CLI command: {e}")
        _refresh_credential(profile)
        return False, '', '', ''
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON output: {e}")
        time.sleep(2)
        return False, '', '', ''
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(2)
        return False, '', '', ''

def _refresh_credential(profile):
        aws_login_command = f'aws sso login --profile {profile}'
        subprocess.check_output(aws_login_command, shell=True, stderr=subprocess.STDOUT)

