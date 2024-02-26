from message import (RunInfoFetchMessage)
import subprocess
import pyperclip
import re
import win32gui
import win32con

hwnd = win32gui.GetForegroundWindow()
win32gui.SetWindowPos(hwnd,win32con.HWND_TOPMOST,1,1,550,500,0)

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

def main(message: RunInfoFetchMessage, info_path: str):
    if message.command and message.switch_1 and message.switch_2:
        _show_content(info_path, message.command, message.switch_1, message.switch_2)
    elif message.command and message.switch_1:
        _show_subtopics(info_path, message.command, message.switch_1)
    elif message.command:
        _show_topics(info_path, message.command)
    else:
        _show_indices(info_path)

def _get_content_lines(info_path) -> list[str]:
    with open(info_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    return lines

def _get_indices(lines) -> tuple[list[str], int]:
    indices = []
    current_line_number = 1
    for line_number, line in enumerate(lines, start=1):
        line = line.strip()
        if line.startswith('Index: '):
            current_index = line[7:].strip().lower()
            indices.append(current_index)
            current_line_number = line_number
    return sorted(indices), current_line_number

def _get_topics(lines, index) -> tuple[list[str], int]:
    topics = []
    current_index = None
    current_line_number = 1
    for line_number, line in enumerate(lines, start=1):
        line = line.strip()
        if line.startswith('Index: '):
            current_index = line[7:].strip().lower()
        elif line.startswith('--- '):
            current_topic = line[4:].strip().lower()
            if current_index and current_index==index:
                topics.append(current_topic)
                current_line_number = line_number
    return sorted(topics), current_line_number

def _get_sub_topics(lines, index, topic) -> tuple[list[str], int]:
    subtopics = []
    current_index = None
    current_topic = None
    current_line_number = 1
    for line_number, line in enumerate(lines, start=1):
        line = line.strip()
        if line.startswith('Index: '):
            current_index = line[7:].strip().lower()
        elif topic and line.startswith('--- '):
            current_topic = line[4:].strip().lower()
        elif line.startswith('@ '):
            current_subtopic = line[1:].strip().lower()
            if current_index==index and current_topic==topic:
                subtopics.append(current_subtopic)
                current_line_number = line_number
    return sorted(subtopics), current_line_number

def _get_content(lines, index, topic, sub_topic) -> tuple[list[str], dict, int]:
    content = []
    current_index = None
    current_topic = None
    current_subtopic = None
    content_ln = 1
    my_line_number = 1
    for line_number, line in enumerate(lines, start=1):
        line = line.strip()
        if line.startswith('Index: '):
            current_index = line[7:].strip().lower()
        elif topic and line.startswith('--- '):
            current_topic = line[4:].strip().lower()
        elif sub_topic and line.startswith('@ '):
            current_subtopic = line[1:].strip().lower()
        elif current_index==index and current_topic==topic and current_subtopic==sub_topic:
            if line:
                content.append(line)
                my_line_number = line_number
                content_ln = content_ln + 1
    return content, my_line_number

def _print_list_with_number(my_list: list) -> None:
    counter = 1
    for item in my_list:
        print(f'{counter}:   {item}')
        counter = counter + 1

def is_int(s) -> bool:
    try:
        int(s)
        return True
    except ValueError:
        return False

def _get_item_in_list(i, my_list) -> str:
    if is_int(i):
        i = my_list[int(i)-1] if (int(i) <= len(my_list) and int(i)>0 ) else None
    if i in my_list:
        return i
    else:
        return None

def _handle_input(info_path, my_list, line_number=1, back=False, to_copy=False):
    browser = ''
    command = input()
    match = re.match(r'^(\d+) (\w+)', command)
    while not _get_item_in_list(command, my_list):
        if command == 'i':
            subprocess.Popen(['start', 'notepad++', f'{info_path}', f'-n{line_number}'], shell=True)
            exit()
        elif command == 'exit' or command == 'e':
            exit()
        elif command == '' and back:
            print('<-')
            break
        elif match:
            command = match.group(1)
            browser_var = match.group(2)
            browser = browser_mapping.get(browser_var, 'unknown')
            break
        else:
            print('Invalid ...')
            command = input()
    output_command = _get_item_in_list(command, my_list)
    if to_copy and output_command:
        if browser == 'chrome':
            subprocess.Popen([f'{chrome_path}', f'{output_command}'], shell=True)
        elif browser == 'edge':
            subprocess.Popen([f'{edge_path}', f'{output_command}'], shell=True)
        else:
            pyperclip.copy(output_command)
    return output_command
    
def _show_indices(info_path):
    lines = _get_content_lines(info_path)
    indices, line_number = _get_indices(lines)
    _print_list_with_number(indices)
    print('-------------')
    index = _handle_input(info_path, indices, line_number, False, False)
    print('-------------')
    _show_topics(info_path, index)

def _show_topics(info_path, index):
    lines = _get_content_lines(info_path)
    if is_int(index):
        indices, _ = _get_indices(lines)
        index = indices[int(index)-1]
    topics, line_number = _get_topics(lines, index)
    if not topics:
        _show_subtopics(info_path, index, None)
    else:
        _print_list_with_number(topics)
        print('-------------')
        topic = _handle_input(info_path, topics, line_number, True, False)
        print('-------------')
        if topic:
            _show_subtopics(info_path, index, topic)
        else:
            _show_indices(info_path)

def _show_subtopics(info_path, index, topic):
    lines = _get_content_lines(info_path)
    if is_int(index):
        indices, _ = _get_indices(lines)
        index = indices[int(index)-1]
    if topic and is_int(topic):
        topics = _get_topics(lines, index)
        topic = topics[int(topic)-1]
    subtopics, line_number = _get_sub_topics(lines, index, topic)
    if not subtopics:
        _show_content(info_path, index, topic, None)
    else:
        _print_list_with_number(subtopics)
        print('-------------')
        sub_topic = _handle_input(info_path, subtopics, line_number, True, False)
        print('-------------')
        if sub_topic:
            _show_content(info_path, index, topic, sub_topic)
        elif topic:
            _show_topics(info_path, index)
        else:
            _show_indices(info_path)

def _show_content(info_path, index, topic, sub_topic):
    lines = _get_content_lines(info_path)
    if is_int(index):
        indices, _ = _get_indices(lines)
        index = indices[int(index)-1]
    if topic and is_int(topic):
        topics, _ = _get_topics(lines, index)
        topic = topics[int(topic)-1]
    if sub_topic and is_int(sub_topic):
        sub_topics, _ = _get_sub_topics(lines, index, topic)
        sub_topic = sub_topics[int(sub_topic)-1]
    content, line_number = _get_content(lines, index, topic, sub_topic)
    _print_list_with_number(content)
    print('-------------')
    content_row = _handle_input(info_path, content, line_number, True, True)
    print('-------------')
    if content_row:
        _show_content(info_path, index, topic, sub_topic)
    elif sub_topic:
        _show_subtopics(info_path, index, topic)
    elif topic:
        _show_topics(info_path, index)
    else:
        _show_indices(info_path)