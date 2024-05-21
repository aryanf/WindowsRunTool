from message import (RunUrlFetchMessage)
import json
import shutil
import sqlite3
import subprocess

def main(message: RunUrlFetchMessage, configuration_path: str):
    with open(configuration_path, 'r') as file:
        config = json.load(file)
    
    count =message.num
    mapper_object = config.get('mapper', [])
    mapper = convert_nested_dict(mapper_object[0])
    browser = _get_browser(config, message.env)
    browser_app_path = browser['app_path']
    browser_history_path = browser['history_path']
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
    if message.env + '0' in mapper:
        url = find_link(browser_history_shadow_path, mapper[message.env + '0'], count, switches)
        url = mapper[message.env + '1'] if url == '' else url
        subprocess.Popen([browser_app_path, url])
    else:
        url = find_link(browser_history_shadow_path, mapper['0'], count, switches)
        url = mapper['1'] if url == '' else url
        subprocess.Popen([browser_app_path, url])


def find_link(browser_history_shadow_path, base_url, count=1, terms=[]):
    con = sqlite3.connect(browser_history_shadow_path)
    cursor = con.cursor()
    if not '@' in base_url:
        return base_url
    terms = [base_url.replace('@', f'%{term}%') for term in terms]
    placeholders = ' and '.join('url LIKE ?' for term in terms)
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
    browser_list = config.get('browsers', [])
    for obj in browser_list:
        if obj['env']==env:
            return obj
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