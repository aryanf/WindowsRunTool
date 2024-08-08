from message import (RunUrlMessage, get_all_env, get_user_name)
import json
import shutil
import sqlite3
import subprocess
import os

def _get_app_path(app_path, app_name):
    if not os.path.exists(app_path):
        if app_name == 'Chrome':
            if os.path.exists('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'):
                return 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
            elif os.path.exists('C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'):
                return 'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'
            else:
                input('Cannot find Chrome browser, update app path in user_configuration.json ...')
                return None
        elif app_name == 'Edge':
            if os.path.exists('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'):
                return 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'
            elif os.path.exists('C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe'):
                return 'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe'
            else:
                input('Cannot find Microsoft Edge browser, update app path in user_configuration.json ...')
                return None
        else:
            input(f'Cannot find {app_name} browser, update app path in user_configuration.json ...')
    else:
        return app_path

def _get_history_path(history_path, app_name):
    if not os.path.exists(history_path):
        username = get_user_name()
        if app_name == 'Chrome':
            if os.path.exists(f'C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1\\History'):
                return f'C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1\\History'
            elif os.path.exists(f'C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History'):
                return f'C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History'
            else:
                input(f'Cannot find {app_name} browser history, update history path in user_configuration.json ...')
                return None
        elif app_name == 'Edge':
            if os.path.exists(f'C:\\Users\\{username}\\AppData\\Local\\Microsoft\\Edge\\User Data\\Profile 1\\History'):
                return f'C:\\Users\\{username}\\AppData\\Local\\Microsoft\\Edge\\User Data\\Profile 1\\History'
            elif os.path.exists(f'C:\\Users\\{username}\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\History'):
                return f'C:\\Users\\{username}\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\History'
            else:
                input(f'Cannot find {app_name} browser history, update history path in user_configuration.json ...')
        else:
            input(f'Cannot find {app_name} browser history, update history path in user_configuration.json ...')
    else:
        return history_path

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
    switches = []
    if message.switch_1:
        switches.append(message.switch_1)
    if message.switch_2:
        switches.append(message.switch_2)
    if message.switch_3:
        switches.append(message.switch_3)

    # update mapper and switches
    if message.command in mapper:
        mapper = mapper[message.command]
        existing_switch = next((switch for switch in switches if switch in mapper), None)
        while existing_switch:
            mapper = mapper[existing_switch]
            switches.remove(existing_switch)
            existing_switch = next((switch for switch in switches if switch in mapper), None)
    else:
        switches.append(message.command)

    # find the url
    url = ''
    url = find_link(browser_history_shadow_path, mapper[message.env][0], count, operator, switches)
    if url == '':
        url = mapper[message.env][1]
        for switch  in switches:
            url = url.replace('@', switch, 1)
    subprocess.Popen([browser_app_path, f'--remote-debugging-port={browser_debug_port}' , url])


def find_link(browser_history_shadow_path, base_url, count=1, operator='and', terms=[]):
    con = sqlite3.connect(browser_history_shadow_path)
    cursor = con.cursor()
    if not '@' in base_url:
        return base_url
    terms = [base_url.replace('@', f'%{term}%') for term in terms] if terms else [base_url.replace('@', '%')]
    placeholders = f' {operator} '.join('url LIKE ?' for term in terms)
    query = f"""
        SELECT DISTINCT url 
        FROM urls 
        WHERE {placeholders}
        ORDER BY last_visit_time DESC 
        LIMIT ?"""
    cursor.execute(query, (*terms, count))
    urls = cursor.fetchall()
    return '' if len(urls)==0 else urls[-1][0]

def _get_browser(config, env):
    all_env = get_all_env()
    env_index = all_env.index(env)
    browser_list = config.get('browsers', [])
    for key, value in browser_list.items():
        if value['env_id']==env_index:
            return value
    print("Cannot read valid env to set the browser")
    input()
    exit()

def convert_nested_dict(d):
    result = {}
    for key, value in d.items():
        if isinstance(value, dict):
            result[key] = convert_nested_dict(value)
        else:
            result[key] = value
    return result