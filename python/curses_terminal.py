import curses
import math

def get_user_input():
    return input("Enter some input: ")

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def show(options, enumerating=False, zero_indexed=False, enable_input=True, info='', item_per_col=30, default_selected_index=0):
    '''
Pass a list to select an item.
Can be shown with prefix number (0-based or 1-based).
Info to describe what user need to select.
Max number of items in a column
return (index, content)
'''
    
    result_content = [None]
    result_index = [None]

    curses.wrapper(get_user_choice, options, enumerating, zero_indexed, lambda x: result_content.__setitem__(0, x), lambda x: result_index.__setitem__(0, x), enable_input, info, item_per_col, default_selected_index)
    return (result_index[0], result_content[0])

def get_user_choice(stdscr, options, enumerating, zero_indexed, set_result_content_callback, set_result_index_callback, enable_input, info, item_per_col, default_selected_index):
    height, width = stdscr.getmaxyx()
    rows = item_per_col if item_per_col < height - 5 else height - 5
    cols = math.ceil(len(options)/rows)
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    selected_row, selected_col = divmod(default_selected_index, rows)
    
    if enumerating:
        temp_options = [f"{i}:  {item}" for i, item in enumerate(options, start=0 if zero_indexed else 1)]
    else:
        temp_options = options

    my_input = ''
    draw_menu(stdscr, selected_row, selected_col, temp_options, rows, cols, enable_input, my_input, info)
    use_arrow = True
    while True:
        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected_row = max(0, selected_row - 1)
        elif key == curses.KEY_DOWN:
            next_col = min(cols - 1, selected_col + 1)
            if next_col == selected_col:  # Check if we're already at the last column
                col_items = min(rows, len(options) - next_col * rows)
                selected_row = min(col_items -1, selected_row + 1)
            else:    
                selected_row = min(rows - 1, selected_row + 1)
        elif key == curses.KEY_LEFT:
            selected_col = max(0, selected_col - 1)
        elif key == curses.KEY_RIGHT:
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
            stdscr.clear()
            if use_arrow:
                index = selected_col * rows + selected_row
                set_result_content_callback(options[index])
                set_result_index_callback(index)
            else:
                if enumerating and is_int(my_input):   
                    set_result_content_callback(options[int(my_input) if zero_indexed else int(my_input)-1])
                    set_result_index_callback(int(my_input) if zero_indexed else int(my_input)-1)
                elif my_input in options:
                    set_result_content_callback(my_input)
                    set_result_index_callback(options.index(my_input))
                else:
                    set_result_content_callback(my_input)
                    set_result_index_callback(None)
            break
        elif key == 8 or key == 127 or key == curses.KEY_BACKSPACE or key == curses.KEY_DC:
            use_arrow = False
            my_input = my_input[:-1]
        elif key == 27:
            set_result_content_callback('exit')
            set_result_index_callback(None)
            break
        else:
            use_arrow = False
            my_input = my_input + chr(key)

        draw_menu(stdscr, selected_row, selected_col, temp_options, rows, cols, enable_input, my_input, info)

def draw_menu(stdscr, selected_row, selected_col, options, rows, cols, enable_input, my_input='', info=''):
    stdscr.clear()
    max_y = 0
    for i, option in enumerate(options):
        col, row = divmod(i, rows)
        x = col * 40 #width // 2 - (cols * 10) // 2 + col * 10
        y = row #height // 2 - (rows * 3) // 2 + row * 3
        if y > max_y:
            max_y = y
        if row == selected_row and col == selected_col:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, option)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, option)

    stdscr.addstr(max_y + 3, 0, info)
    if enable_input:
        stdscr.addstr(max_y + 5, 0, my_input)
    stdscr.refresh()