import curses
import math
from typing import List, Tuple
import time

# Constants colors to be used in other parts of the code
# Define color constants
COLOR_WHITE = curses.COLOR_WHITE
COLOR_RED = curses.COLOR_RED
COLOR_GREEN = curses.COLOR_GREEN
COLOR_BLUE = curses.COLOR_BLUE
COLOR_YELLOW = curses.COLOR_YELLOW
COLOR_CYAN = curses.COLOR_CYAN
COLOR_MAGENTA = curses.COLOR_MAGENTA
COLOR_BLACK = curses.COLOR_BLACK
COLOR_8 = 8
COLOR_9 = 9
COLOR_10 = 10
COLOR_11 = 11
COLOR_12 = 12
INACTIVITY_TIMEOUT = 600  # seconds, after which the menu will close if no input is received


def get_user_input(message=''):
    if message:
        return input(message)
    else:
        return input("Enter some input: ")

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def show(
        options_colors: List[tuple] =[], commands_colors: List[tuple]=[], options: List[str]=[], commands: List[str]=[],
        enumerating=True, zero_indexed=False, enable_input=True, info='',
        item_per_col=30, default_selected_index=0, scrollable=False):
    '''
Pass a list to select an item.
Can be shown with prefix number (0-based or 1-based).
Info to describe what user need to select.
Max number of items in a column
return (index, content)
'''
    result_content = [None]
    result_index = [None]
    if options and not options_colors:
        options_colors = [(option, COLOR_WHITE) for option in options]
    if commands and not commands_colors:
        commands_colors = [(command, COLOR_WHITE) for command in commands]

    temp_default_selected_index = default_selected_index
    if scrollable:
        curses.wrapper(get_user_choice_scrollable, options_colors, commands_colors, enumerating, zero_indexed,
                    lambda x: result_content.__setitem__(0, x), lambda x: result_index.__setitem__(0, x),
                    enable_input, info, default_selected_index + 1)
    else:
        curses.wrapper(get_user_choice, options_colors, commands_colors, enumerating, zero_indexed,
                lambda x: result_content.__setitem__(0, x), lambda x: result_index.__setitem__(0, x),
                enable_input, info, item_per_col, default_selected_index)
    
    if result_content[0]== 's':
        scrollable = not scrollable
        return show(options_colors, commands_colors, options, commands, enumerating, zero_indexed,
                    enable_input, info, item_per_col, temp_default_selected_index, scrollable)

    return (result_index[0], result_content[0])


def get_user_choice(stdscr, options, commands, enumerating, zero_indexed, set_result_content_callback,
                    set_result_index_callback, enable_input, info, item_per_col, default_selected_index):
    height, width = stdscr.getmaxyx()
    #if scrollable:
    rows = item_per_col if item_per_col < height - 5 else height - 5
    cols = math.ceil(len(options)/rows)
    selected_row = default_selected_index
    selected_col = 0
    options = options + commands
    
    if enumerating:
        enumerated_options = [(f"{i}:  {item[0]}", item[1]) for i, item in enumerate(options, start=0 if zero_indexed else 1)]
    else:
        enumerated_options = options
    my_input = ''
    draw_menu(stdscr, selected_row, selected_col, enumerated_options, rows, cols, enable_input, my_input, info)

    last_input_time = time.time()
    stdscr.timeout(60000) 
    use_arrow = True
    while True:
        key = stdscr.getch()

        if key == curses.KEY_UP:
            last_input_time = time.time()
            selected_row = max(0, selected_row - 1)
        elif key == curses.KEY_DOWN:
            last_input_time = time.time()
            next_col = min(cols - 1, selected_col + 1)
            if next_col == selected_col:  # Check if we're already at the last column
                col_items = min(rows, len(options) - next_col * rows)
                selected_row = min(col_items -1, selected_row + 1)
            else:    
                selected_row = min(rows - 1, selected_row + 1)
        elif key == curses.KEY_LEFT:
            last_input_time = time.time()
            selected_col = max(0, selected_col - 1)
        elif key == curses.KEY_RIGHT:
            last_input_time = time.time()
            next_col = min(cols - 1, selected_col + 1)
            if next_col == selected_col:  # Check if we're already at the last column
                selected_col = next_col
            else:
                next_col_items = min(rows, len(options) - next_col * rows)  # Number of items in the next column
                if selected_row < next_col_items:
                    selected_col = next_col
                    selected_row = min(selected_row, next_col_items - 1)
            # selected_col = min(cols - 1, selected_col + 1)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            last_input_time = time.time()
            stdscr.clear()
            if use_arrow:
                index = selected_col * rows + selected_row
                set_result_content_callback(options[index][0])
                set_result_index_callback(index)
            else:
                if enumerating and is_int(my_input):   
                    set_result_content_callback(options[int(my_input) if zero_indexed else int(my_input)-1][0])
                    set_result_index_callback(int(my_input) if zero_indexed else int(my_input)-1)
                elif my_input in options:
                    set_result_content_callback(my_input)
                    set_result_index_callback(options.index(my_input))
                else:
                    set_result_content_callback(my_input)
                    set_result_index_callback(None)
            break
        elif key == 8 or key == 127 or key == curses.KEY_BACKSPACE or key == curses.KEY_DC:
            last_input_time = time.time()
            use_arrow = False
            my_input = my_input[:-1]
        elif key == 27:
            last_input_time = time.time()
            set_result_content_callback('exit')
            set_result_index_callback(None)
            break
        elif key == -1:
            if time.time() - last_input_time > INACTIVITY_TIMEOUT:
                set_result_content_callback('exit')
                set_result_index_callback(None)
                break
            continue
        else:
            last_input_time = time.time()
            use_arrow = False
            my_input = my_input + chr(key)

        draw_menu(stdscr, selected_row, selected_col, enumerated_options, rows, cols, enable_input, my_input, info)

def draw_menu(stdscr, selected_row, selected_col, options, rows, cols, enable_input, my_input='', info=''):
    
    curses.init_color(8, 150, 150, 300)
    curses.init_color(9, 250, 250, 350)
    curses.init_color(10, 400, 400, 550)
    curses.init_color(11, 300, 500, 550)
    curses.init_color(12, 500, 300, 550)

    # convert extra colors to white if not supported
    if not curses.can_change_color():
        for i, option in enumerate(options):
            if color[1] > 7:
                options[i][1] = curses.COLOR_WHITE

    # Maximum width for each option based on number of columns
    width = stdscr.getmaxyx()[1]
    max_width = width // cols - 2
    col_spacing = max_width + 2 

    # Truncate options if necessary
    def truncate_txt(txt):
        return txt if len(txt) <= max_width else txt[:max_width - 3] + "..."

    truncated_options = [(truncate_txt(option[0]), option[1]) for option in options]

    # get distinct colors
    distinct_colors = set([truncated_option[1] for truncated_option in truncated_options])
    for i, color in enumerate(distinct_colors):
        curses.init_pair(color, color, curses.COLOR_BLACK)
    selected_color = 20
    curses.init_pair(selected_color, curses.COLOR_BLACK, curses.COLOR_WHITE)
    
    stdscr.clear()
    max_y = 0
    
    for i, option in enumerate(truncated_options):
        color = option[1]
        col, row = divmod(i, rows)
        x = col * col_spacing
        y = row 
        if y > max_y:
            max_y = y
        if row == selected_row and col == selected_col:
            stdscr.attron(curses.color_pair(selected_color))
            stdscr.addstr(y, x, str(option[0]))
            stdscr.attroff(curses.color_pair(selected_color))
        else:
            stdscr.attron(curses.color_pair(color))
            stdscr.addstr(y, x, str(option[0]))
            stdscr.attroff(curses.color_pair(color))

    stdscr.addstr(max_y + 3, 0, info)
    if enable_input:
        stdscr.addstr(max_y + 5, 0, my_input)
    stdscr.refresh()

def get_user_choice_scrollable(stdscr, options, commands, enumerating, zero_indexed, set_result_content_callback,
                    set_result_index_callback, enable_input, info, default_selected_index):
    height, width = stdscr.getmaxyx()
    rows = height - 5
    cols = 2
    selected_row = default_selected_index
    selected_col = 0
    
    if enumerating:
        enumerated_options = [(f"{i}:  {item[0]}", item[1]) for i, item in enumerate(options, start=0 if zero_indexed else 1)]
        command_index_start = len(enumerated_options)
        enumerated_commands = [('', curses.COLOR_WHITE)] + [(f"{i+command_index_start}:  {item[0]}", item[1]) for i, item in enumerate(commands, start=0 if zero_indexed else 1)]
    else:
        enumerated_options = options
        enumerated_commands = [('', curses.COLOR_WHITE)] + commands
    my_input = ''

    arrow_up = ('   ˄   ', curses.COLOR_WHITE)
    arrow_down = ('   ˅   ', curses.COLOR_WHITE)
    empty_row = ('', curses.COLOR_WHITE)
    
    scrolling = False
    if len(enumerated_options) > rows-2:
        scrolling = True
    
    if scrolling:
        scrolling_options =  [empty_row]+enumerated_options[0:rows-2]+[arrow_down]
    else:
        scrolling_options = [empty_row]+enumerated_options+[empty_row]

    my_input = ''
    draw_menu_scrollable(stdscr, selected_row, selected_col, scrolling_options, enumerated_commands, rows, cols, enable_input, my_input, info)
    i = 0
    use_arrow = True
    total_items = len(enumerated_options)
    visible_items = rows - 2  # room for up/down arrows

    last_input_time = time.time()
    stdscr.timeout(60000) 

    while True:
        key = stdscr.getch()

        if key == curses.KEY_DOWN:
            last_input_time = time.time()
            if selected_col == 0:
                max_scroll_index = total_items - visible_items + 1

                # If not scrolling, move within range
                if not scrolling:
                    if selected_row < total_items:
                        selected_row += 1
                else:
                    if selected_row < visible_items:
                        # move down within window
                        selected_row += 1
                    elif i < max_scroll_index - 1:
                        # scroll down
                        i += 1

                    # Recalculate visible slice
                    top_arrow = [arrow_up] if i > 0 else [empty_row]
                    bottom_arrow = [arrow_down] if i + visible_items < total_items else [empty_row]
                    scrolling_slice = enumerated_options[i:i + visible_items]
                    scrolling_options = top_arrow + scrolling_slice + bottom_arrow
            else:
                selected_row = min(len(commands), selected_row + 1)
        elif key == curses.KEY_UP:
            last_input_time = time.time()
            if selected_col == 0:
                if not scrolling:
                    if selected_row > 1:
                        selected_row -= 1
                else:
                    if selected_row > 1:
                        # move up within window
                        selected_row -= 1
                    elif i > 0:
                        # scroll up
                        i -= 1

                    # Recalculate visible slice
                    top_arrow = [arrow_up] if i > 0 else [empty_row]
                    bottom_arrow = [arrow_down] if i + visible_items < total_items else [empty_row]
                    scrolling_slice = enumerated_options[i:i + visible_items]
                    scrolling_options = top_arrow + scrolling_slice + bottom_arrow
            else:
                selected_row = max(1, selected_row - 1)
        elif key == curses.KEY_LEFT:
            last_input_time = time.time()
            if commands:
                if selected_col == 0:
                    if selected_row == 0 or selected_row > len(enumerated_commands) - 1:
                        selected_col = 0
                    else:
                        selected_col = 1
                else:
                    if selected_row > len(scrolling_options) - 1:
                        selected_col = 1
                    else:
                        selected_col = 0
        elif key == curses.KEY_RIGHT:
            last_input_time = time.time()
            if commands:
                if selected_col == 0:
                    if selected_row == 0 or selected_row > len(enumerated_commands) - 1:
                        selected_col = 0
                    else:
                        selected_col = 1
                else:
                    if selected_row > len(scrolling_options) - 1:
                        selected_col = 1
                    else:
                        selected_col = 0
        elif key == curses.KEY_ENTER or key in [10, 13]:
            last_input_time = time.time()
            stdscr.clear()
            if use_arrow:
                if selected_col == 0:
                    index = i + selected_row - 1
                    set_result_content_callback(options[index][0])
                    set_result_index_callback(index)
                else:
                    index = -1
                    set_result_content_callback(commands[selected_row-1][0])
                    set_result_index_callback(index)
            else:
                if enumerating and is_int(my_input):   
                    set_result_content_callback(options[int(my_input) if zero_indexed else int(my_input)-1][0])
                    set_result_index_callback(int(my_input) if zero_indexed else int(my_input)-1)
                elif my_input in options:
                    set_result_content_callback(my_input)
                    set_result_index_callback(options.index(my_input))
                else:
                    set_result_content_callback(my_input)
                    set_result_index_callback(None)
            break
        elif key == 8 or key == 127 or key == curses.KEY_BACKSPACE or key == curses.KEY_DC:
            last_input_time = time.time()
            use_arrow = False
            my_input = my_input[:-1]
        elif key == 27:
            last_input_time = time.time()
            set_result_content_callback('exit')
            set_result_index_callback(None)
            break
        elif key == -1:
            if time.time() - last_input_time > INACTIVITY_TIMEOUT:
                set_result_content_callback('exit')
                set_result_index_callback(None)
                break
            continue
        else:
            last_input_time = time.time()
            use_arrow = False
            my_input = my_input + chr(key)

        draw_menu_scrollable(stdscr, selected_row, selected_col, scrolling_options, enumerated_commands, rows, cols, enable_input, my_input, info)

def draw_menu_scrollable(stdscr, selected_row, selected_col, options, commands, rows, cols, enable_input, my_input='', info=''):
    cols = 2
    curses.init_color(8, 150, 150, 300)
    curses.init_color(9, 250, 250, 350)
    curses.init_color(10, 400, 400, 550)
    curses.init_color(11, 300, 500, 550)
    curses.init_color(12, 500, 300, 550)

    # convert extra colors to white if not supported
    if not curses.can_change_color():
        for i, option in enumerate(options):
            if option[1] > 7:
                options[i][1] = curses.COLOR_WHITE

    if not curses.can_change_color():
        for i, command in enumerate(commands):
            if command[1] > 7:
                command[i][1] = curses.COLOR_WHITE

    # Maximum width for each option based on number of columns
    width = stdscr.getmaxyx()[1]
    max_width = width // cols - 2
    col_spacing = max_width + 2 

    # Truncate options if necessary
    def truncate_txt(txt):
        return txt if len(txt) <= max_width else txt[:max_width - 3] + "..."

    truncated_options = [(truncate_txt(option[0]), option[1]) for option in options]
    truncated_commands = [(truncate_txt(command[0]), command[1]) for command in commands]

    # get distinct colors
    distinct_colors = set([option_command[1] for option_command in truncated_options+truncated_commands])
    for i, color in enumerate(distinct_colors):
        curses.init_pair(color, color, curses.COLOR_BLACK)
    selected_color = 20
    curses.init_pair(selected_color, curses.COLOR_BLACK, curses.COLOR_WHITE)
    
    stdscr.clear()
    max_y = 0

    for i, option in enumerate(truncated_options):
        color = option[1]
        col, row = divmod(i, rows)
        x = col * col_spacing
        y = row 
        if y > max_y:
            max_y = y
        if row == selected_row and col == selected_col:
            stdscr.attron(curses.color_pair(selected_color))
            stdscr.addstr(y, x, option[0])
            stdscr.attroff(curses.color_pair(selected_color))
        else:
            stdscr.attron(curses.color_pair(color))
            stdscr.addstr(y, x, option[0])
            stdscr.attroff(curses.color_pair(color))

    for i, command in enumerate(truncated_commands):
        color = command[1]
        col, row = divmod(i, rows)
        col = col + 1
        x = col * col_spacing
        y = row 
        if y > max_y:
            max_y = y
        if row == selected_row and col == selected_col:
            stdscr.attron(curses.color_pair(selected_color))
            stdscr.addstr(y, x, command[0])
            stdscr.attroff(curses.color_pair(selected_color))
        else:
            stdscr.attron(curses.color_pair(color))
            stdscr.addstr(y, x, command[0])
            stdscr.attroff(curses.color_pair(color))


    stdscr.addstr(max_y + 3, 0, info)
    if enable_input:
        stdscr.addstr(max_y + 5, 0, my_input)
    stdscr.refresh()

