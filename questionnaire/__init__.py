from collections import OrderedDict
from itertools import islice
import operator
import inspect

from .prompters import prompters


class Condition:
    """Container for condition properties.
    """
    OPERATORS = {
        '==' : operator.eq,
        '!=' : operator.ne,
        '>'  : operator.lt,
        '<'  : operator.gt,
        '<=' : operator.le,
        '>=' : operator.ge,
        }

    def __init__(self, keys=[], vals=[], operators=[]):
        self.keys = list(keys)
        self.vals = list(vals)
        self.operators = list(operators) if operators \
            else ['==']*len(self.keys)

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
                print("Condition has invalid operator(s). Operators must " \
                "accept two args. Hint: to define your own, use lamdbas")
                raise


class Question:
    """Container for question properties. The key looks up the prompter in the
    prompters registry. Additional keyword args are passed along to prompter.
    """
    def __init__(self, key, prompter="single", prompt="", **prompter_args):
        self.key = key
        self.condition = None

        assert prompter in prompters, "This prompter doesn't exist"
        self.prompter = prompters[prompter]
        self.prompter_args = prompter_args

    def run_prompter(self):
        self.prompter(self.prompter_args)

    def add_condition(self, **kwargs):
        if 'keys' in kwargs and 'vals' in kwargs:
            self.condition = Condition(**kwargs)
        return self.condition


class Questionnaire:
    """Class with methods for adding questions to a questionnaire, and running
    the questionnaire. Additional keyword args are passed any prompter method
    when it is called.
    """
    def __init__(self, show_choices=True):
        self.questions = OrderedDict() # key -> list of Question instances
        self.choices = OrderedDict() # key -> option(s)
        self._show_choices = show_choices

    def show_choices(self, s=""):
        """Helper method for displaying the choices made so far.
        """
        padding = len(max(self.questions.keys(), key=len)) + 5
        for key in list(self.choices.keys()):
            s += "{:>{}} : {}\n".format(key, padding, self.choices[key])
        return s

    def add_question(self, *args, **kwargs):
        """Add a Question instance to the questions dict. Each key points
        to a list of Question instances with that key.
        """
        question = Question(*args, **kwargs)
        self.questions.setdefault(question.key, []).append(question)
        return question

    def run(self):
        """Prompt the user to choose one or more options for each question
        in the questionnaire, and return the choices.
        """
        self.choices = OrderedDict() # reset choices
        while True:
            if not self.ask_questions():
                continue
            return dict(self.choices)

    def ask_questions(self):
        """Helper that asks questions in questionnaire, and returns
        False if user "goes back".
        """
        for key in self.questions.keys():
            question = self.which_question(key)
            if question is not None and key not in self.choices:
                if not self.ask_question(question):
                    return False
        return True

    # def prompt(self, key, options, prompt="", kind="single"):
    def ask_question(self, q):
        """Call the question's prompter, and check to see if user goes back.
        """
        prompt = q.prompt if hasattr(q, 'prompt') else "{}: ".format(q.key)
        if self.show_choices:
            prompt = self.show_choices() + "\n{}".format(prompt)

        self.choices[q.key], back = q.prompter(prompt, **q.prompter_args)
        if back is not None:
            self.go_back(abs(int(back)))
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
        for key, val, op in \
            zip(condition.keys, condition.vals, condition.operators):
            if not op(self.choices[key], val):
                return False
        return True

    def go_back(self, n=1):
        """Move `n` questions back in the questionnaire, and remove
        the last `n` choices.
        """
        N = max(len(self.choices)-n-1, 0)
        self.choices = OrderedDict(islice(self.choices.items(), N))
