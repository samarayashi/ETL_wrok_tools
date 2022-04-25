"""This module is for splitting string"""
import logging

open_tup = "({["
close_tup = ")}]"
bracket_map = dict(zip(open_tup, close_tup))


def bracket_excluded_char_split(raw_str: str, sep_char: str) -> list[str]:
    """Sql_string enumerate the columns.
    Want to get every single column from it, but need to avoid split the comma in the bracket.
    Only accept one char to be splitting symbol, return a list of column string"""

    if len(sep_char) > 1:
        raise ValueError('sep_char only can accept one char value.')

    check_stack = []
    parenthese_close = True
    start_char_index = 0
    separate_words = []
    for idx, char in enumerate(raw_str):
        if char in open_tup:
            check_stack.append(bracket_map[char])
            if len(check_stack) == 1:
                parenthese_close = False

        elif char in close_tup:
            if not check_stack or check_stack.pop() != char:
                logging.warning("!! bracket unpair, please check correct or not.")
            if len(check_stack) == 0:
                parenthese_close = True

        if parenthese_close and char == sep_char:
            separate_words.append(raw_str[start_char_index: idx])
            start_char_index = idx+1
    else:
        separate_words.append(raw_str[start_char_index:])
        
    return separate_words
