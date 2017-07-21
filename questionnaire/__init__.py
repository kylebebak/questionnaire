import operator
import inspect
import sys
from collections import OrderedDict
from itertools import islice
from functools import wraps
import json

from .prompters import prompters


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
                print("Condition has invalid operator(s). Operators must "
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
            assert prompter in prompters, "This is not a core prompter"
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
    def __init__(self, show_answers=True, dump_to_array=False):
        self.questions = OrderedDict()  # key -> list of Question instances
        self.answers = OrderedDict()  # key -> answer
        self._show_answers = show_answers
        self.dump_to_array = dump_to_array

    def show_answers(self, s=""):
        """Helper method for displaying the answers so far.
        """
        padding = len(max(self.questions.keys(), key=len)) + 5
        for key in list(self.answers.keys()):
            s += "{:>{}} : {}\n".format(key, padding, self.answers[key])
        return s

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

    @exit_on_keyboard_interrupt
    def run(self):
        """Prompt the user to answer each question in the questionnaire, then
        print the answers to stdout and return them.
        """
        self.answers = OrderedDict()  # reset answers
        while True:
            if not self.ask_questions():
                continue
            if self.dump_to_array:
                answers = [[k, v] for k, v in self.answers.items()]
                print(json.dumps(answers))
            else:
                print(json.dumps(self.answers))  # print answers to stdout, and return them
            return self.answers

    def ask_questions(self):
        """Helper that asks questions in questionnaire, and returns
        False if user "goes back".
        """
        for key in self.questions.keys():
            question = self.which_question(key)
            if question is not None and key not in self.answers:
                if not self.ask_question(question):
                    return False
        return True

    def ask_question(self, q):
        """Call the question's prompter, and check to see if user goes back.
        """
        prompt = q.prompt
        if self._show_answers:
            prompt = self.show_answers() + "\n{}".format(q.prompt)

        self.answers[q.key], back = q.prompter(prompt, **q.prompter_args)
        if back is None:
            return True
        if back == '':  # super hacky =/
            self.go_back(0)
            return False
        if back < 0:
            self.go_back(abs(back))
            return False
        return True

    def which_question(self, key):
        """Decide which Question instance to select from the list of questions
        corresponding to the key, based on condition. Returns first question
        for which condition is satisfied, or for which there is no condition.
        """
        questions = self.questions[key]
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
        """Move `n` questions back in the questionnaire, and remove
        the last `n` answers.
        """
        N = max(len(self.answers)-n-1, 0)
        self.answers = OrderedDict(islice(self.answers.items(), N))
