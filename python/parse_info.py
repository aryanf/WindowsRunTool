from message import (RunInfoMessage)
import subprocess
import pyperclip
import win32gui
import win32con
import curses_terminal
import validators

hwnd = win32gui.GetForegroundWindow()
win32gui.SetWindowPos(hwnd,win32con.HWND_TOP,1,1,900,800,0)

chrome_path = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
edge_path = 'C:\\Program Files (x86)\\Microsoft\\edge\\Application\\msedge.exe'
browser_mapping = {
    'c': 'chrome',
    'ch': 'chrome',
    'chrome': 'chrome',
    'chmoe': 'chrome',
    'chrom': 'chrome',
    'e': 'edge',
    'ed': 'edge',
    'ege': 'edge',
    'edg': 'edge',
    'edge': 'edge'
}

def main(message: RunInfoMessage, info_path: str, user_path: str):
    if message.command and message.switch_1 and message.switch_2:
        _show_content(info_path, message.command, message.switch_1, message.switch_2)
    elif message.command and message.switch_1:
        _show_subtopics(info_path, message.command, message.switch_1)
    elif message.command:
        _show_topics(info_path, message.command)
    else:
        _show_titles(info_path)

def _get_content_lines(info_path) -> list[str]:
    with open(info_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    return lines

def _get_titles(lines) -> tuple[list[str], int]:
    titles = []
    current_line_number = 1
    for line_number, line in enumerate(lines, start=1):
        line = line.strip()
        if line.startswith('Index: '):
            current_index = line[7:].strip().lower()
            titles.append(current_index)
            current_line_number = line_number
    return sorted(titles), current_line_number

def _get_topics(lines, title) -> tuple[list[str], int]:
    topics = []
    current_title = None
    current_line_number = 1
    for line_number, line in enumerate(lines, start=1):
        line = line.strip()
        if line.startswith('Index: '):
            current_title = line[7:].strip().lower()
        elif line.startswith('--- '):
            current_topic = line[4:].strip().lower()
            if current_title and current_title==title:
                topics.append(current_topic)
                current_line_number = line_number
    return sorted(topics), current_line_number

def _get_sub_topics(lines, title, topic) -> tuple[list[str], int]:
    subtopics = []
    current_title = None
    current_topic = None
    current_line_number = 1
    for line_number, line in enumerate(lines, start=1):
        line = line.strip()
        if line.startswith('Index: '):
            current_title = line[7:].strip().lower()
        elif topic and line.startswith('--- '):
            current_topic = line[4:].strip().lower()
        elif line.startswith('@ '):
            current_subtopic = line[1:].strip().lower()
            if current_title==title and current_topic==topic:
                subtopics.append(current_subtopic)
                current_line_number = line_number
    return sorted(subtopics), current_line_number

def _get_content(lines, title, topic, sub_topic) -> tuple[list[str], dict, int]:
    content = []
    current_title = None
    current_topic = None
    current_subtopic = None
    content_ln = 1
    my_line_number = 1
    for line_number, line in enumerate(lines, start=1):
        line = line.strip()
        if line.startswith('Index: '):
            current_title = line[7:].strip().lower()
        elif topic and line.startswith('--- '):
            current_topic = line[4:].strip().lower()
        elif sub_topic and line.startswith('@ '):
            current_subtopic = line[1:].strip().lower()
        elif current_title==title and current_topic==topic and current_subtopic==sub_topic:
            if line:
                content.append(line)
                my_line_number = line_number
                content_ln = content_ln + 1
    return content, my_line_number

def _show(my_list: list) -> None:
    my_list.insert(0, '..')
    return curses_terminal.show(my_list, enumerating=True, zero_indexed=True)

def _is_int(s) -> bool:
    try:
        int(s)
        return True
    except ValueError:
        return False


def _handle_input(command, info_path, my_list, line_number=1, to_copy=False):
    if command == 'i':
        subprocess.Popen(['start', 'notepad++', f'{info_path}', f'-n{line_number}'], shell=True)
        exit()
    elif command == 'exit' or command == 'e':
        exit()
    else:
        browser = browser_mapping.get(command, 'chrome')
        return browser


def _show_titles(info_path):
    lines = _get_content_lines(info_path)
    titles, line_number = _get_titles(lines)
    i, cmd = _show(titles)
    if i == None:
        _ = _handle_input(cmd, info_path, titles, line_number, False)
    if i == 0:
        _show_titles(info_path)
    else:
        _show_topics(info_path, i)    


def _show_topics(info_path, title):
    lines = _get_content_lines(info_path)
    if _is_int(title):
        titles, _ = _get_titles(lines)
        title = titles[int(title)-1]
    topics, line_number = _get_topics(lines, title)
    if not topics:
        _show_subtopics(info_path, title, None)
    else:
        i, cmd = _show(topics)
        if i == None:
            _ = _handle_input(cmd, info_path, topics, line_number, False)
        if i == 0:
            _show_titles(info_path)
        else:
            _show_subtopics(info_path, title, i)

def _show_subtopics(info_path, title, topic):
    lines = _get_content_lines(info_path)
    if _is_int(title):
        titles, _ = _get_titles(lines)
        title = titles[int(title)-1]
    if topic and _is_int(topic):
        topics, _ = _get_topics(lines, title)
        topic = topics[int(topic)-1]
    subtopics, line_number = _get_sub_topics(lines, title, topic)
    if not subtopics:
        _show_content(info_path, title, topic, None)
    else:
        i, cmd = _show(subtopics)
        if i == None:
            _ = _handle_input(cmd, info_path, subtopics, line_number, False)
        if topic and i == 0:
            _show_topics(info_path, title)
        elif i == 0:
            _show_titles(info_path)
        else:
            _show_content(info_path, title, topic, i)
        

def _show_content(info_path, title, topic, sub_topic, browser='chrome'):
    lines = _get_content_lines(info_path)
    if _is_int(title):
        titles, _ = _get_titles(lines)
        title = titles[int(title)-1]
    if topic and _is_int(topic):
        topics, _ = _get_topics(lines, title)
        topic = topics[int(topic)-1]
    if sub_topic and _is_int(sub_topic):
        sub_topics, _ = _get_sub_topics(lines, title, topic)
        sub_topic = sub_topics[int(sub_topic)-1]
    content, line_number = _get_content(lines, title, topic, sub_topic)
    i, cmd =_show(content)
    if i == None:
        browser = _handle_input(cmd, info_path, content, line_number, True)
        _show_content(info_path, title, topic, sub_topic, browser=browser)
    if sub_topic and i == 0:
        _show_subtopics(info_path, title, topic)
    elif topic and i == 0:
        _show_topics(info_path, title)
    elif i == 0:
        _show_titles(info_path)
    else:
        if validators.url(cmd):
            if browser == 'chrome':
                subprocess.Popen([f'{chrome_path}', f'{cmd}'], shell=True)
            elif browser == 'edge':
                subprocess.Popen([f'{edge_path}', f'{cmd}'], shell=True)
        else:
            pyperclip.copy(cmd)
        _show_content(info_path, title, topic, sub_topic, browser=browser)