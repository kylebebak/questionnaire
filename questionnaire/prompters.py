"""All prompters registered in this module must have a function signature
of (prompt="", **kwargs), and must return an (answer, back) tuple, even if
a back event doesn't occur. If the value for back is an int, the
questionnaire will go back that number of questions.

Extending questionnaire is as simple writing your own prompter and passing
it to `add_question`.
"""
import sys
import curses

from pick import Picker


prompters = {}

def register(key="function"):
    """Add decorated functions to prompters dict.
    """
    def decorate(func):
        prompters[key] = func
        return func
    return decorate


@register(key="single")
def single(prompt="", **kwargs):
    """Instantiates a picker, registers custom handlers for going back,
    and starts the picker.
    """
    def go_back(picker):
        return None, -1
    options = kwargs["options"] if "options" in kwargs else []

    picker = Picker(options, title=prompt, indicator='=>')
    picker.register_custom_handler(ord('h'), go_back)
    picker.register_custom_handler(curses.KEY_LEFT, go_back)
    option, i = picker.start()
    if i < 0: # user went back
        return option, 1
    return option, None


@register(key="multiple")
def multiple(prompt="", **kwargs):
    """Calls `pick` in a while loop to allow user to pick multiple
    options. Returns a list of chosen options.
    """
    ALL = kwargs["all"] if "all" in kwargs else "all"
    DONE = kwargs["done"] if "done" in kwargs else "done..."
    options = kwargs["options"] if "options" in kwargs else []
    options = [ALL] + options + [DONE] if ALL else options + [DONE]
    options_ = []
    while True:
        option, i = single('{}{}'.format(prompt, options_), options=options)
        if type(i) is int: # user went back
            return (options_, 0) if options_ else (options_, 1)
        if ALL and option == ALL:
            return ([ALL], None)
        if option == DONE:
            return (options_, None)
        options_.append(option)
        options.remove(option)


@register(key="raw")
def raw(prompt="", **kwargs):
    """Calls input to allow user to input an arbitrary string. User can go
    back by entering the `go_back` string. Works in both Python 2 and 3.
    """
    go_back = kwargs["go_back"] if "go_back" in kwargs else "<"
    type_ = kwargs["type"] if "type" in kwargs else str
    while True:
        try:
            answer = eval('raw_input(prompt)') if sys.version_info < (3, 0) \
                                               else eval('input(prompt)')
            return (answer, 1) if answer == go_back else (type_(answer), None)
        except ValueError:
            print("\n`{}` is not a valid `{}`\n".format(answer, type_))
