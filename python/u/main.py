from message import (RunMessage)
import json
import shutil
import sqlite3
import subprocess

def main(message: RunMessage, configuration_path: str):
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


    if message.command in mapper:
        mapper = mapper[message.command]
        if message.switch_1 in mapper:
            mapper = mapper[message.switch_1]
            if message.switch_2 in mapper:
                mapper = mapper[message.switch_2]
                url = find_link(browser_history_shadow_path, mapper['0'], count, message.switch_3)
                url = mapper['1'] if url == '' else url
                subprocess.Popen([browser_app_path, url])
            else:
                url = find_link(browser_history_shadow_path, mapper['0'], count, message.switch_2, message.switch_3)
                print(url)
                url = mapper['1'] if url == '' else url
                subprocess.Popen([browser_app_path, url])
        else:
            url = find_link(browser_history_shadow_path, mapper['0'], count, message.switch_1, message.switch_2, message.switch_3)
            url = mapper['1'] if url == '' else url
            subprocess.Popen([browser_app_path, url])
    else:
        url = find_link(browser_history_shadow_path, mapper['0'], count, message.command, message.switch_1, message.switch_2, message.switch_3)
        url = mapper['1'] if url == '' else url
        subprocess.Popen([browser_app_path, url])


def find_link(browser_history_shadow_path, base_url, count=1, term1=None, term2=None, term3=None, term4=None):
    con = sqlite3.connect(browser_history_shadow_path)
    cursor = con.cursor()

    if term4:    
        term1 = base_url.replace('@', f'%{term1}%')
        term2 = base_url.replace('@', f'%{term2}%')
        term3 = base_url.replace('@', f'%{term3}%')
        term4 = base_url.replace('@', f'%{term4}%')
        query = """
            SELECT DISTINCT url 
            FROM urls 
            WHERE url LIKE ? and url LIKE ? and url LIKE ? and url LIKE ? 
            ORDER BY last_visit_time DESC 
            LIMIT ?"""
        cursor.execute(query, (term1, term2, term3, term4, count))
    elif term3:    
        term1 = base_url.replace('@', f'%{term1}%')
        term2 = base_url.replace('@', f'%{term2}%')
        term3 = base_url.replace('@', f'%{term3}%')
        query = """
            SELECT DISTINCT url 
            FROM urls 
            WHERE url LIKE ? and url LIKE ? and url LIKE ? 
            ORDER BY last_visit_time DESC 
            LIMIT ?"""
        cursor.execute(query, (term1, term2, term3, count))
    elif term2:    
        term1 = base_url.replace('@', f'%{term1}%')
        term2 = base_url.replace('@', f'%{term2}%')
        query = """
            SELECT DISTINCT url 
            FROM urls 
            WHERE url LIKE ? and url LIKE ?
            ORDER BY last_visit_time DESC 
            LIMIT ?"""
        cursor.execute(query, (term1, term2, count))
    elif term1:    
        term1 = base_url.replace('@', f'%{term1}%')
        query = """
            SELECT DISTINCT url 
            FROM urls 
            WHERE url LIKE ?
            ORDER BY last_visit_time DESC 
            LIMIT ?"""
        cursor.execute(query, (term1, count))
    else:
        return ''
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