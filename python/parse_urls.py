from message import (RunUrlMessage, get_all_env, get_user_name)
import json
import shutil
import sqlite3
import subprocess
import os
from win10toast import ToastNotifier

def _get_app_path(app_path, app_name):
    if os.path.exists(app_path):
        return app_path
    username = get_user_name()
    chrome_paths = [
        f'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
        f'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'
    ]
    edge_paths = [
        f'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
        f'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe'
    ]
    opera_paths = [
        f'C:\\Users\\{username}\\AppData\\Local\\Programs\\Opera\\opera.exe'
    ]

    if app_name == 'Chrome':
        for path in chrome_paths:
            if os.path.exists(path):
                return path
    elif app_name == 'Edge':
        for path in edge_paths:
            if os.path.exists(path):
                return path    
    elif app_name == 'Opera':
        for path in opera_paths:
            if os.path.exists(path):
                return path

    input(f'Cannot find {app_name} browser, update app path in user_configuration.json ...')
    return None

def _get_history_path(history_path, app_name):
    if os.path.exists(history_path):
        return history_path

    username = get_user_name()
    chrome_history_paths = [
        f'C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1\\History',
        f'C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History'
    ]
    edge_history_paths = [
        f'C:\\Users\\{username}\\AppData\\Local\\Microsoft\\Edge\\User Data\\Profile 1\\History',
        f'C:\\Users\\{username}\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\History'
    ]
    opera_history_paths = [
        f'C:\\Users\\{username}\\AppData\\Roaming\\Opera Software\\Opera Stable\\Default\\History'
    ]

    if app_name == 'Chrome':
        for path in chrome_history_paths:
            if os.path.exists(path):
                return path
    elif app_name == 'Edge':
        for path in edge_history_paths:
            if os.path.exists(path):
                return path
    elif app_name == 'Opera':
        for path in opera_history_paths:
            if os.path.exists(path):
                return path

    input(f'Cannot find {app_name} browser history, update history path in user_configuration.json ...')
    return None

def main(message: RunUrlMessage, url_path: str, user_path: str):
    with open(url_path, 'r') as url_file:
        mapper = json.load(url_file)
    with open(user_path, 'r') as user_file:
        user_config = json.load(user_file)
    
    count = message.num
    operator = message.operator
    browser = _get_browser(user_config, message.env)
    browser_debug_port = browser['debug_port']
    browser_name = browser['app_name']
    browser_app_path = _get_app_path(browser['app_path'], browser_name)
    browser_history_path = _get_history_path(browser['history_path'], browser_name)
    browser_history_shadow_path = browser_history_path + '-Shadow'
    shutil.copy(browser_history_path, browser_history_shadow_path)
    switches = [message.switch_1, message.switch_2, message.switch_3]
    switches = [switch for switch in switches if switch]

    # Update mapper and switches
    if message.command in mapper:
        mapper = mapper[message.command]
        existing_switch = next((switch for switch in switches if switch in mapper), None)
        while existing_switch:
            mapper = mapper[existing_switch]
            switches.remove(existing_switch)
            existing_switch = next((switch for switch in switches if switch in mapper), None)
    else:
        switches.append(message.command)

    # Find the url
    url = ''
    url = find_link(browser_history_shadow_path, mapper[message.env][0], count, operator, switches)
    if url == '':
        url = mapper[message.env][1]
        for switch  in switches:
            url = url.replace('@', switch, 1)

    subprocess.Popen([browser_app_path, f'--remote-debugging-port={browser_debug_port}' , url])


def remove_common_parts(strings):
    if not strings:
        return []
    # Find the common prefix
    common_prefix = os.path.commonprefix(strings)
    # Remove the common prefix from each string
    result = [s[len(common_prefix):] for s in strings]
    return result

def move_index_to_start(lst, number):
    index = number - 1  # Calculate the desired index (number - 1)
    if 0 <= index < len(lst):  # Check if the index is valid
        # Remove the item at the index and insert it at the start
        item = lst.pop(index)
        lst.insert(0, item)
    return lst

def find_link(browser_history_shadow_path, base_url, count=1, operator='and', terms=[]):
    with sqlite3.connect(browser_history_shadow_path) as con:
        cursor = con.cursor()
        if '@' not in base_url:
            return base_url
        terms = [base_url.replace('@', f'%{term}%') for term in terms] if terms else [base_url.replace('@', '%')]
        placeholders = f' {operator} '.join('url LIKE ?' for term in terms)
        query = f"""
            SELECT DISTINCT url 
            FROM urls 
            WHERE {placeholders}
            ORDER BY last_visit_time DESC"""
        cursor.execute(query, (terms))
        urls = cursor.fetchall()
        output = remove_common_parts([x[0] for x in urls])
        output = move_index_to_start(output, int(count))
        toaster = ToastNotifier()
        toaster.show_toast(f'{len(urls)} urls', '\n'.join([x[:40] for x in output]) , duration=10, threaded=True)
        return '' if not urls else urls[int(count)-1][0]

def _get_browser(config, env):
    all_env = get_all_env()
    env_index = all_env.index(env)
    browser_list = config.get('browsers', [])
    for key, value in browser_list.items():
        if value['env_id'] == env_index:
            return value
    print("Cannot read valid env to set the browser")
    input()
    exit()

def convert_nested_dict(d):
    return {key: convert_nested_dict(value) if isinstance(value, dict) else value for key, value in d.items()}