import operator
import inspect
import sys
from collections import OrderedDict
from itertools import islice
from functools import wraps
import json

from .prompters import prompters, eprint, QuestionnaireGoBack


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

    def __init__(self, keys=[], vals=[], operators=[]):
        self.keys = list(keys)
        self.vals = list(vals)
        self.operators = list(operators) if operators else ['==']*len(self.keys)

        vars = [self.keys, self.vals, self.operators]
        assert all(type(var) == list for var in vars), \
            "All condition properties must be lists"
        assert all(len(var) == len(vars[0]) for var in vars), \
            "All condition properties must have the same length"
        self.assign_operators()

    def assign_operators(self):
        """Assigns function to the operators property of the instance.
        """
        for i, op in enumerate(self.operators):
            if op in Condition.OPERATORS:
                self.operators[i] = Condition.OPERATORS[op]
                continue
            try:
                n_args = len(inspect.getargspec(op)[0])
                return n_args == 2
            except:
                eprint("Error: Condition has invalid operator(s). Operators must "
                       "accept two args. Hint: to define your own, use lamdbas")
                raise


class Question:
    """Container for question properties. A string key will look up the
    prompter in the core prompters registry, or you can pass your own
    prompter method that conforms to the prompter API.
    """
    def __init__(self, key, prompter="single", prompt="", **prompter_args):
        self.key = key
        self.condition = None
        self.assign_prompter(prompter)
        self.assign_prompt(prompt)
        self.prompter_args = prompter_args

    def assign_prompter(self, prompter):
        """If you want to change the core prompters registry, you can
        override this method in a Question subclass.
        """
        if type(prompter) is str:
            if prompter not in prompters:
                eprint("Error: '{}' is not a core prompter".format(prompter))
                sys.exit()
            self.prompter = prompters[prompter]
        else:
            self.prompter = prompter

    def assign_prompt(self, prompt):
        self.prompt = prompt.strip() + " " if prompt else "{}: ".format(self.key)

    def add_condition(self, **kwargs):
        if 'keys' in kwargs and 'vals' in kwargs:
            self.condition = Condition(**kwargs)
        return self.condition


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

    def add_question(self, *args, **kwargs):
        """Add a Question instance to the questions dict. Each key points
        to a list of Question instances with that key. Use the `question`
        kwarg to pass a Question instance if you want, or pass in the same
        args you would pass to instantiate a question.
        """
        if "question" in kwargs and isinstance(kwargs["question"], Question):
            question = kwargs["question"]
        else:
            question = Question(*args, **kwargs)
        self.questions.setdefault(question.key, []).append(question)
        return question

    def run(self):
        """Asks all remaining questions in the questionnaire, returns the answers.
        """
        while not self.done:
            self.ask_question()
        return self.answers

    @exit_on_keyboard_interrupt
    def ask_question(self):
        """Asks the next question in the questionnaire and returns the answer,
        unless user goes back.
        """
        q = self.next_question
        if q is None:
            return

        prompt = q.prompt
        if self.show_answers:
            prompt = self.answer_display() + "\n{}".format(q.prompt)

        try:
            answer = q.prompter(prompt, **q.prompter_args)
        except QuestionnaireGoBack as e:
            self.go_back(e.args[0] if e.args else 1)
        else:
            self.answers[q.key] = answer
            return answer

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
                if self.check_condition(question.condition):
                    return question
        return None

    def check_condition(self, condition):
        """Helper that returns True if condition is satisfied/doesn't exist.
        """
        if not condition:
            return True
        for key, val, op in zip(condition.keys, condition.vals, condition.operators):
            if not op(self.answers[key], val):
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

    def answer_display(self, s=""):
        """Helper method for displaying the answers so far.
        """
        padding = len(max(self.questions.keys(), key=len)) + 5
        for key in list(self.answers.keys()):
            s += "{:>{}} : {}\n".format(key, padding, self.answers[key])
        return s
