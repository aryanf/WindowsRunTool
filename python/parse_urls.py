from message import (RunUrlMessage, get_all_env)
import json
import shutil
import sqlite3
import subprocess

def main(message: RunUrlMessage, url_path: str, user_path: str):
    with open(url_path, 'r') as url_file:
        mapper = json.load(url_file)
    with open(user_path, 'r') as user_file:
        user_config = json.load(user_file)
    
    count = message.num
    operator = message.operator
    browser = _get_browser(user_config, message.env)
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
                if message.env in mapper:
                    url = find_link(browser_history_shadow_path, mapper[message.env][0], count, operator, message.switch_3)
                    url = mapper[message.env][1] if url == '' else url
                    subprocess.Popen([browser_app_path, url])
                else:
                    print(f"Correct url mapper cannot be found for {message.env} env")
                    input()
            else:
                if message.env in mapper:
                    url = find_link(browser_history_shadow_path, mapper[message.env][0], count, operator, message.switch_2, message.switch_3)
                    url = mapper[message.env][1] if url == '' else url
                    subprocess.Popen([browser_app_path, url])
                else:
                    print(f"Correct url mapper cannot be found for {message.env} env")
                    input()
        else:
            if message.env in mapper:
                url = find_link(browser_history_shadow_path, mapper[message.env][0], count, operator, message.switch_1, message.switch_2, message.switch_3)
                url = mapper[message.env][1] if url == '' else url
                subprocess.Popen([browser_app_path, url])
            else:
                print(f"Correct url mapper cannot be found for {message.env} env")
                input()
    else:
        if message.env in mapper:
            url = find_link(browser_history_shadow_path, mapper[message.env][0], count, operator, message.command, message.switch_1, message.switch_2, message.switch_3)
            url = mapper[message.env][1] if url == '' else url
            subprocess.Popen([browser_app_path, url])
        else:
            print(f"Correct url mapper cannot be found for {message.env} env")
            input()


def find_link(browser_history_shadow_path, base_url, count=1, operator='and', term1=None, term2=None, term3=None, term4=None):
    con = sqlite3.connect(browser_history_shadow_path)
    cursor = con.cursor()
    if not '@' in base_url:
        return base_url
    if term4:    
        term1 = base_url.replace('@', f'%{term1}%')
        term2 = base_url.replace('@', f'%{term2}%')
        term3 = base_url.replace('@', f'%{term3}%')
        term4 = base_url.replace('@', f'%{term4}%')
        query = f"""
            SELECT DISTINCT url 
            FROM urls 
            WHERE url LIKE ? {operator} url LIKE ? {operator} url LIKE ? {operator} url LIKE ? 
            ORDER BY last_visit_time DESC 
            LIMIT ?"""
        cursor.execute(query, (term1, term2, term3, term4, count))
    elif term3:    
        term1 = base_url.replace('@', f'%{term1}%')
        term2 = base_url.replace('@', f'%{term2}%')
        term3 = base_url.replace('@', f'%{term3}%')
        query = f"""
            SELECT DISTINCT url 
            FROM urls 
            WHERE url LIKE ? {operator} url LIKE ? {operator} url LIKE ? 
            ORDER BY last_visit_time DESC 
            LIMIT ?"""
        cursor.execute(query, (term1, term2, term3, count))
    elif term2:    
        term1 = base_url.replace('@', f'%{term1}%')
        term2 = base_url.replace('@', f'%{term2}%')
        query = f"""
            SELECT DISTINCT url 
            FROM urls 
            WHERE url LIKE ? {operator} url LIKE ?
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
        term = base_url.replace('@', f'%%')
        query = """
            SELECT DISTINCT url 
            FROM urls 
            WHERE url LIKE ?
            ORDER BY last_visit_time DESC 
            LIMIT ?"""
        cursor.execute(query, (term, count))
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