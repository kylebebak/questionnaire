"""All prompters registered in this module must return an (answer, back)
tuple, even if a back event doesn't occur. If the value for back is an
int, the questionnaire will move back that number of questions.

Extending questionnaire is as simple as defining a valid prompter in this
module and decorating it with @register.
"""

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
    ALL = kwargs["ALL"] if "ALL" in kwargs else "all"
    DONE = kwargs["DONE"] if "DONE" in kwargs else "done..."
    options = kwargs["options"] if "options" in kwargs else []
    options, options_ = [ALL] + options + [DONE], []
    while True:
        option, i = single('{}{}'.format(prompt, options_), options=options)
        if type(i) is int: # user went back
            return (options_, 0) if options_ else (options_, 1)
        if option == ALL:
            return ([ALL], None)
        if option == DONE:
            return (options_, None)
        options_.append(option)
        options.remove(option)


@register(key="raw")
def raw(prompt="", **kwargs):
    """Calls input to allow user to input an arbitrary string. User can go
    back by entering the `go_back` string.
    """
    go_back = kwargs["go_back"] if "go_back" in kwargs else "<"
    type_ = kwargs["type"] if "type" in kwargs else str
    while True:
        try:
            answer = input(prompt)
            return (answer, 1) if answer == go_back else (type_(answer), None)
        except ValueError:
            print("`{}` is not a valid `{}`".format(answer, type_))
