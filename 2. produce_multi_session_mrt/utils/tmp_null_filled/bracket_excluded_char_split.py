import logging

open_tup = "({["
close_tup = ")}]"
bracket_map = dict(zip(open_tup, close_tup))


def bracket_excluded_char_split(string: str, sep_char: str)->list:

    if len(sep_char) > 1:
        raise ValueError('sep_char only can accept one char value.')

    check_stack = []
    parenthese_close = True
    first_char_index = 0
    separate_words = []
    for idx, char in enumerate(string):
        if char in open_tup:
            check_stack.append(bracket_map[char])
            if len(check_stack) > 0:
                parenthese_close = False

        elif char in close_tup:
            if not check_stack or check_stack.pop() != char:
                logging.warning("!! bracket unpair, please check correct or not.")
            if len(check_stack) ==0:
                parenthese_close = True

        if parenthese_close and char == sep_char:
            separate_words.append(string[first_char_index: idx])
            first_char_index = idx+1
    else:
        separate_words.append(string[first_char_index:])
        
    return separate_words
