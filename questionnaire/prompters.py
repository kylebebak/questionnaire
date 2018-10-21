# -*- coding: utf-8 -*-
"""All prompters registered in this module must have a function signature of
(prompt, *args, **kwargs), and must return an answer. If a back event occurs, the
prompter should raise `QuestionnaireGoBack`.

Extending questionnaire is as simple writing your own prompter and passing it to
`add`.
"""
from __future__ import print_function
import sys
import curses
import os
import getpass
from contextlib import contextmanager

from pick import Picker


prompters = {}


class QuestionnaireGoBack(Exception):
    """Signals user went back instead of answering question."""


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def is_string(thing):
    if sys.version_info < (3, 0):
        return isinstance(thing, basestring)
    return isinstance(thing, str)


def register(key='function'):
    """Add decorated functions to prompters dict.
    """
    def decorate(func):
        prompters[key] = func
        return func
    return decorate


@register(key='one')
def one(prompt, *args, **kwargs):
    """Instantiates a picker, registers custom handlers for going back,
    and starts the picker.
    """
    indicator = '‣'
    if sys.version_info < (3, 0):
        indicator = '>'

    def go_back(picker):
        return None, -1

    options, verbose_options = prepare_options(args)
    idx = kwargs.get('idx', 0)

    picker = Picker(verbose_options, title=prompt, indicator=indicator, default_index=idx)
    picker.register_custom_handler(ord('h'), go_back)
    picker.register_custom_handler(curses.KEY_LEFT, go_back)
    with stdout_redirected(sys.stderr):
        option, index = picker.start()
        if index == -1:
            raise QuestionnaireGoBack
        if kwargs.get('return_index', False):
            # `one` was called by a special client, e.g. `many`
            return index
        return options[index]


@register(key='many')
def many(prompt, *args, **kwargs):
    """Calls `pick` in a while loop to allow user to pick many
    options. Returns a list of chosen options.
    """
    def get_options(options, chosen):
        return [options[i] for i, c in enumerate(chosen) if c]

    def get_verbose_options(verbose_options, chosen):
        no, yes = ' ', '✔'
        if sys.version_info < (3, 3):
            no, yes = ' ', '@'
        opts = ['{} {}'.format(yes if c else no, verbose_options[i]) for i, c in enumerate(chosen)]
        return opts + ['{}{}'.format('  ', kwargs.get('done', 'done...'))]

    options, verbose_options = prepare_options(args)
    chosen = [False] * len(options)
    index = kwargs.get('idx', 0)

    default = kwargs.get('default', None)
    if isinstance(default, list):
        for idx in default:
            chosen[idx] = True
    if isinstance(default, int):
        chosen[default] = True

    while True:
        try:
            index = one(prompt, *get_verbose_options(verbose_options, chosen), return_index=True, idx=index)
        except QuestionnaireGoBack:
            if any(chosen):
                raise QuestionnaireGoBack(0)
            else:
                raise QuestionnaireGoBack
        if index == len(options):
            return get_options(options, chosen)
        chosen[index] = not chosen[index]


def prepare_options(options):
    """Create options and verbose options from strings and non-string iterables in
    `options` array.
    """
    options_, verbose_options = [], []
    for option in options:
        if is_string(option):
            options_.append(option)
            verbose_options.append(option)
        else:
            options_.append(option[0])
            verbose_options.append(option[1])
    return options_, verbose_options


@register(key='raw')
def raw(prompt, *args, **kwargs):
    """Calls input to allow user to input an arbitrary string. User can go
    back by entering the `go_back` string. Works in both Python 2 and 3.
    """
    go_back = kwargs.get('go_back', '<')
    type_ = kwargs.get('type', str)
    default = kwargs.get('default', '')
    with stdout_redirected(sys.stderr):
        while True:
            try:
                if kwargs.get('secret', False):
                    answer = getpass.getpass(prompt)
                elif sys.version_info < (3, 0):
                    answer = raw_input(prompt)
                else:
                    answer = input(prompt)

                if not answer:
                    answer = default

                if answer == go_back:
                    raise QuestionnaireGoBack
                return type_(answer)
            except ValueError:
                eprint('\n`{}` is not a valid `{}`\n'.format(answer, type_))


@contextmanager
def stdout_redirected(to):
    """Lifted from: https://stackoverflow.com/questions/4675728/redirect-stdout-to-a-file-in-python

    This is the only way I've found to redirect stdout with curses. This way the
    output from questionnaire can be piped to another program, without piping
    what's written to the terminal by the prompters.
    """
    stdout = sys.stdout

    stdout_fd = fileno(stdout)
    # copy stdout_fd before it is overwritten
    with os.fdopen(os.dup(stdout_fd), 'wb') as copied:
        stdout.flush()  # flush library buffers that dup2 knows nothing about
        try:
            os.dup2(fileno(to), stdout_fd)  # $ exec >&to
        except ValueError:  # filename
            with open(to, 'wb') as to_file:
                os.dup2(to_file.fileno(), stdout_fd)  # $ exec > to
        try:
            yield stdout  # allow code to be run with the redirected stdout
        finally:
            # restore stdout to its previous value
            stdout.flush()
            os.dup2(copied.fileno(), stdout_fd)


def fileno(file_or_fd):
    fd = getattr(file_or_fd, 'fileno', lambda: file_or_fd)()
    if not isinstance(fd, int):
        raise ValueError('Expected a file (`.fileno()`) or a file descriptor')
    return fd
