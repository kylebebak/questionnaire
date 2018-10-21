# -*- coding: utf-8 -*-
import operator
import inspect
import json
import sys
from collections import namedtuple, OrderedDict
from itertools import islice
from functools import wraps

from .prompters import prompters, eprint, QuestionnaireGoBack, is_string


Cond = namedtuple('Cond', 'key, value, operator')


def exit_on_keyboard_interrupt(f):
    """Decorator that allows user to exit script by sending a keyboard interrupt
    (ctrl + c) without raising an exception.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        raise_exception = kwargs.pop('raise_exception', False)
        try:
            return f(*args, **kwargs)
        except KeyboardInterrupt:
            if not raise_exception:
                sys.exit()
            raise KeyboardInterrupt
    return wrapper


class Condition:
    """Container for condition properties.
    """
    OPERATORS = {
        '==': operator.eq,
        '!=': operator.ne,
        '>': operator.lt,
        '<': operator.gt,
        '<=': operator.le,
        '>=': operator.ge,
    }

    def __init__(self, *args):
        self.conditions = []
        for condition in args:
            if len(condition) == 2:
                condition = list(condition) + ['==']
            key, value, operator = condition
            self.conditions.append(Cond(key, value, self.get_operator(operator)))

    def get_operator(self, op):
        """Assigns function to the operators property of the instance.
        """
        if op in self.OPERATORS:
            return self.OPERATORS.get(op)
        try:
            n_args = len(inspect.getargspec(op)[0])
            if n_args != 2:
                raise TypeError
        except:
            eprint('Error: invalid operator function. Operators must accept two args.')
            raise
        else:
            return op


class Question:
    """Container for question properties. A string key will look up the
    prompter in the core prompters registry, or you can pass your own
    prompter method that conforms to the prompter API.
    """
    def __init__(self, key, *args, **kwargs):
        self.key = key
        self._condition = None
        self._validate = None
        self._transform = None
        self.assign_prompter(kwargs.pop('prompter'))  # `prompter` required
        self.assign_prompt(kwargs.pop('prompt', None), kwargs.get('default', None))  # `prompt`, `default` optional
        self.prompter_args = args
        self.prompter_kwargs = kwargs

    def assign_prompter(self, prompter):
        """If you want to change the core prompters registry, you can
        override this method in a Question subclass.
        """
        if is_string(prompter):
            if prompter not in prompters:
                eprint("Error: '{}' is not a core prompter".format(prompter))
                sys.exit()
            self.prompter = prompters[prompter]
        else:
            self.prompter = prompter

    def assign_prompt(self, prompt, default=None):
        self.prompt = prompt.strip() + ' ' if prompt else '{}: '.format(self.key)
        if default is not None:
            self.prompt += '[{}] '.format(default)

    def condition(self, *args):
        self._condition = Condition(*args)
        return self

    def validate(self, f):
        self._validate = f
        return self

    def transform(self, f):
        self._transform = f
        return self


class Questionnaire:
    """Class with methods for adding questions to a questionnaire, and running
    the questionnaire. Additional keyword args are passed to the prompter
    method when it is called.
    """
    def __init__(self, show_answers=True, can_go_back=True):
        self.questions = OrderedDict()  # key -> list of Question instances
        self.answers = OrderedDict()  # key -> answer
        self.show_answers = show_answers
        self.can_go_back = can_go_back

    def add(self, *args, **kwargs):
        """Add a Question instance to the questions dict. Each key points
        to a list of Question instances with that key. Use the `question`
        kwarg to pass a Question instance if you want, or pass in the same
        args you would pass to instantiate a question.
        """
        if 'question' in kwargs and isinstance(kwargs['question'], Question):
            question = kwargs['question']
        else:
            question = Question(*args, **kwargs)
        self.questions.setdefault(question.key, []).append(question)
        return question

    def one(self, *args, **kwargs):
        kwargs['prompter'] = 'one'
        return self.add(*args, **kwargs)

    def many(self, *args, **kwargs):
        kwargs['prompter'] = 'many'
        return self.add(*args, **kwargs)

    def raw(self, *args, **kwargs):
        kwargs['prompter'] = 'raw'
        return self.add(*args, **kwargs)

    def remove(self, key):
        """Remove all questions associated with `key`. Raises exception if `key`
        doesn't exist.
        """
        return self.questions.pop(key)

    def run(self):
        """Asks all remaining questions in the questionnaire, returns the answers.
        """
        while not self.done:
            self.ask()
        return self.answers

    @exit_on_keyboard_interrupt
    def ask(self, error=None):
        """Asks the next question in the questionnaire and returns the answer,
        unless user goes back.
        """
        q = self.next_question
        if q is None:
            return

        try:
            answer = q.prompter(self.get_prompt(q, error), *q.prompter_args, **q.prompter_kwargs)
        except QuestionnaireGoBack as e:
            steps = e.args[0] if e.args else 1
            if steps == 0:
                self.ask()  # user can redo current question even if `can_go_back` is `False`
                return
            self.go_back(steps)
        else:
            if q._validate:
                error = q._validate(answer)
                if error:
                    self.ask(error)
                    return
            if q._transform:
                answer = q._transform(answer)
            self.answers[q.key] = answer
            return answer

    def get_prompt(self, question, error=None):
        parts = []
        if self.show_answers:
            parts.append(self.answer_display())
        if error:
            parts.append(error)
        parts.append(question.prompt)
        return '\n\n'.join(str(p) for p in parts)

    @property
    def next_question(self):
        """Returns the next `Question` in the questionnaire, or `None` if there
        are no questions left. Returns first question for whose key there is no
        answer and for which condition is satisfied, or for which there is no
        condition.
        """
        for key, questions in self.questions.items():
            if key in self.answers:
                continue
            for question in questions:
                if self.check_condition(question._condition):
                    return question
        return None

    def check_condition(self, condition):
        """Helper that returns True if condition is satisfied/doesn't exist.
        """
        if not condition:
            return True
        for c in condition.conditions:
            key, value, operator = c
            if not operator(self.answers[key], value):
                return False
        return True

    def go_back(self, n=1):
        """Move `n` questions back in the questionnaire by removing the last `n`
        answers.
        """
        if not self.can_go_back:
            return
        N = max(len(self.answers)-abs(n), 0)
        self.answers = OrderedDict(islice(self.answers.items(), N))

    @property
    def done(self):
        return self.next_question is None

    def reset(self):
        self.answers = OrderedDict()

    def format_answers(self, fmt='obj'):
        """Formats answers depending on `fmt`.
        """
        fmts = ('obj', 'array', 'plain')
        if fmt not in fmts:
            eprint("Error: '{}' not in {}".format(fmt, fmts))
            return

        def stringify(val):
            if type(val) in (list, tuple):
                return ', '.join(str(e) for e in val)
            return val

        if fmt == 'obj':
            return json.dumps(self.answers)
        elif fmt == 'array':
            answers = [[k, v] for k, v in self.answers.items()]
            return json.dumps(answers)
        elif fmt == 'plain':
            answers = '\n'.join('{}: {}'.format(k, stringify(v)) for k, v in self.answers.items())
            return answers

    def answer_display(self, s=''):
        """Helper method for displaying the answers so far.
        """
        padding = len(max(self.questions.keys(), key=len)) + 5
        for key in list(self.answers.keys()):
            s += '{:>{}} : {}\n'.format(key, padding, self.answers[key])
        return s
