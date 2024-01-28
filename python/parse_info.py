from message import (RunInfoFetchMessage)
import subprocess
import pyperclip
import win32gui
import win32con

hwnd = win32gui.GetForegroundWindow()
win32gui.SetWindowPos(hwnd,win32con.HWND_TOPMOST,1,1,550,500,0)

def main(message: RunInfoFetchMessage, info_path: str):
    if message.command and message.switch_1:
        _parse_info_file_show_content(info_path, message.command, message.switch_1)
    elif message.command:
        _parse_info_file_show_subtopics(info_path, message.command)
    else:
        _parse_info_file_show_topics(info_path)

def _get_content_lines(info_path):
    with open(info_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    return lines

def _get_topics(lines) -> list[str]:
    current_topic = None
    topics = []
    for line in lines:
        line = line.strip()
        if line.startswith('--- '):
            current_topic = line[4:].strip().lower()
            topics.append(current_topic)
    return sorted(topics)

def _get_sub_topics_and_line_num(lines, topic) -> (list[str], int):
    current_line_number = 1
    subtopics = []
    current_topic = None
    for line_number, line in enumerate(lines, start=1):
        line = line.strip()
        if line.startswith('--- '):
            current_topic = line[4:].strip().lower()
        elif line.startswith('@ '):
            current_subtopic = line[1:].strip().lower()
            if current_topic:
                if(current_topic==topic):
                    subtopics.append(current_subtopic)
                    current_line_number = line_number
    return subtopics, current_line_number

def _get_content_and_line_num(lines, topic, sub_topic) -> (list[str], dict, int):
    current_topic = None
    current_subtopic = None
    content_ln_line = {}
    content = []
    content_ln = 1
    my_line_number = 1
    for line_number, line in enumerate(lines, start=1):
        line = line.strip()
        if line.startswith('--- '):
            current_topic = line[4:].strip().lower()
        elif line.startswith('@ '):
            current_subtopic = line[1:].strip().lower()
        elif current_topic and current_subtopic:
            if(current_topic==topic and current_subtopic==sub_topic):
                if line:
                    content.append(line)
                    my_line_number = line_number
                    content_ln_line[content_ln] = line_number
                    content_ln = content_ln + 1
    return content, content_ln_line, my_line_number

def _print_list_with_number(mylist: list):
    counter = 1
    for item in mylist:
        print(f'{counter}:   {item}')
        counter = counter + 1

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def _get_item_in_list(i, my_list):
    if is_int(i):
        i = my_list[int(i)-1] if (int(i) <= len(my_list) and int(i)>0 ) else None
    if i in my_list:
        return i
    else:
        return None

def _handle_input(info_path, my_list, line_number=1, back=False, to_copy=False):
    command = input()
    while not _get_item_in_list(command, my_list):
        if command == 'i':
            subprocess.Popen(['start', 'notepad++', f'{info_path}', f'-n{line_number}'], shell=True)
            exit()
        elif command == 'exit' or command == 'e':
            exit()
        elif command == '' and back:
            print('<-')
            break
        else:
            print('Invalid ...')
            command = input()
    output_command = _get_item_in_list(command, my_list)
    if to_copy and output_command:
        pyperclip.copy(output_command)
    return output_command
    

def _parse_info_file_show_topics(info_path):
    lines = _get_content_lines(info_path)
    topics = _get_topics(lines)
    _print_list_with_number(topics)
    print('-------------')
    topic = _handle_input(info_path, topics, 1, False, False)
    print('-------------')
    _parse_info_file_show_subtopics(info_path, topic)


def _parse_info_file_show_subtopics(info_path, topic):
    lines = _get_content_lines(info_path)
    if is_int(topic):
        topics = _get_topics(lines)
        topic = topics[int(topic)-1]
    sub_topics, line_number = _get_sub_topics_and_line_num(lines, topic)
    _print_list_with_number(sub_topics)
    print('-------------')
    sub_topic = _handle_input(info_path, sub_topics, line_number, True, False)
    print('-------------')
    if sub_topic:
        _parse_info_file_show_content(info_path, topic, sub_topic)
    else:
        _parse_info_file_show_topics(info_path)


def _parse_info_file_show_content(info_path, topic, sub_topic):
    lines = _get_content_lines(info_path)
    if is_int(topic):
        topics = _get_topics(lines)
        topic = topics[int(topic)-1]
    if is_int(sub_topic):
        sub_topics, _ = _get_sub_topics_and_line_num(lines, topic)
        sub_topic = sub_topics[int(sub_topic)-1]
    content, content_ln_line, line_number = _get_content_and_line_num(lines, topic, sub_topic)
    _print_list_with_number(content)
    print('-------------')
    content_row = _handle_input(info_path, content, line_number, True, True)
    print('-------------')
    if content_row:
        _parse_info_file_show_content(info_path, topic, sub_topic)
    else:
        _parse_info_file_show_subtopics(info_path, topic)