# questionnaire

![License](https://camo.githubusercontent.com/890acbdcb87868b382af9a4b1fac507b9659d9bf/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f6c6963656e73652d4d49542d626c75652e737667)

__questionnaire__ is a mini-DSL for writing command line questionnaires. It prompts a user to answer a series of questions and returns the answers.

__questionnaire__ is simple and powerful. Some features: 

- Compact, intuitive syntax
- Composable: pipe answers to other programs as JSON or plain text
- Powerful and flexible
  + Conditional questions can depend on previous answers
  + Allow users to reanswer questions
  + Validate and transform answers
  + Question presentation decoupled from answer values
  + Run all remaining questions or ask them one at a time
    * [Extend questionnaire as it's being run](#github-api)
- __choose one__, __choose many__, and __raw input__ prompters built in
  + Extend questionnaire by writing your own prompter


## Installation
__questionnaire__ is written in Python. It works with Python 2 and 3, although it's a bit prettier if you run it with Python 3. The best way to install it is with `pip`.

~~~sh
pip install questionnaire
~~~


## Getting Started
Paste the following into a file and save it. Let's assume you save it as `questions.py`. Go to the command line and run `python questions.py`.

~~~py
# questions.py
from questionnaire import Questionnaire
q = Questionnaire()

q.one('day', 'monday', 'friday', 'saturday', prompt='What day is it?')
q.one('time', ('morning', 'in the morning'), ('night', 'at night'), prompt='What time is it?')

q.run()
print(q.format_answers())
~~~

What's happening here? We instantiate a questionnaire with `q = Questionnaire()`, add two questions to it, and run the questionnaire. At the end the answers are printed to stdout as JSON.

Look at the second question with the __"time"__ key. We pass tuples for our options instead of strings. The first value in these tuples is the answer value stored by the questionnaire, and the second value is the option presented to the user. In other words, the presentation of your questionnaire __can be decoupled from the answers it returns__.


### Getting Fancy
Add a group of conditional questions to the questionnaire above. Only one of these questions will be asked, depending on the answers to the first two questions. Run the questionnaire with `python questions.py`, and inspect the answers as well.

~~~py
# questions.py
from questionnaire import Questionnaire
q = Questionnaire()

q.one('day', 'monday', 'friday', 'saturday')
q.one('time', 'morning', 'night')

q.many('activities', 'eat tacos de pastor', 'go to the cantina', 'do some programming').condition(('time', 'night'))
q.many('activities', 'eat barbacoa', 'watch footy', 'walk the dog').condition(('day', 'saturday'), ('time', 'morning'))
q.many('activities', 'eat granola', 'get dressed', 'go to work').condition(('time', 'morning'))

q.run()
print(q.format_answers(fmt='array'))
~~~

![](https://raw.githubusercontent.com/kylebebak/questionnaire/master/examples/activities_client.gif)

As you can see, it's easy to print answers to stdout. In keeping with the [UNIX philosophy](https://en.wikipedia.org/wiki/Unix_philosophy), __Questionnaire is composable__. If you don't want to write Python code, you can write a standalone questionnaire that pipes its answers to another program for handling. If you want to handle them in the same script, just reference `q.answers`, which is a nice `OrderedDict`.

Also, did you notice the `fmt='array'` argument? This formats the answers as a JSON array instead of a JSON object. This guarantees parsing the answers doesn't screw up their order, although it might make parsing more cumbersome.


#### Plain Text
If you plan on piping the results of a questionnaire to a shell script, you might want plain text instead of JSON. Just pass `fmt='plain'` when you format the answers to your `Questionnaire`. The answers will be returned as plain text, one answer per line.


### GitHub API
Here's another example. This one handles raw input. It first prompts the user for their GitHub __username__ and __password__. Then it pauses the questionnaire and uses these credentials to hit the GitHub API to get a list of all their repos. Finally, it adds another question to the questionnaire and resumes it, prompting the user to choose one of these repos.

It depends on the [Requests](https://github.com/requests/requests) library, so install it if you want to give it a try. First, add a question using the `raw` prompter.

~~~py
from questionnaire import Questionnaire
import requests

q = Questionnaire(show_answers=False, can_go_back=False)
q.raw('user', prompt='Username:')
q.raw('pass', prompt='Password:', secret=True)

q.run()
r = requests.get('https://api.github.com/user/repos', auth=(q.answers.get('user'), q.answers.get('pass')))
if not(r.ok):
    import sys
    print('username/password incorrect')
    sys.exit()

repos = [repo.get('url') for repo in r.json()]
q.one('repo', *repos, prompt='Choose a repo')
q.run()
print(q.answers.get('repo'))

~~~


## More Examples
Check out clients in the `examples` directory.


## Prompters
The core prompters are currently `one`, `many`, `raw`. The first two depend on the excellent [pick](https://github.com/wong2/pick) package. All three are used in the examples above.


## One Option
To require the user to pick one option from a list, invoke `questionnaire.one`. When the question is answered the chosen option is added to the `answers` dict.


### Many Options
To allow the user to pick many options for a single question, invoke `questionnaire.many`. When the question is answered, the list of chosen options is added to the `answers` dict. As with the `one` prompter, users can use <kbd>&larr;</kbd> or <kbd>h</kbd> to go back.


### Raw Input
For raw input, invoke `questionnaire.raw`. Optionally pass a `type` (`int`, `float`, ...) to coerce the answer to a given type. By default, the user can go back from a raw input question by entering `<` as the answer. To change this, pass your own `go_back` string.

If you want to capture password input, or any other secret input, pass `secret=True`.


## Validating and Transforming Answers
__questionnaire__ makes validating and transforming answers a cinch. For validation, you chain a call to `validate` onto a question and pass a validation function. When the user answers, the validation function receives one argument (the answer).

If there's anything wrong with the answer, the function __should return a string explaining what's wrong__. The explanation is shown to the user when he submits an invalid answer. If there's nothing wrong with the answer, the function shouldn't return anything.

_Transforming_ answers is very similar. Chain a call to `transform` onto a question and pass a transform function. This function receives the answer as an argument. It should do something with it and return a transformed answer. The transformed answer is the one that will actually be saved in the questionnaire. See how you can use __questionnaire__ to help your users sign up for junk mail.

~~~py
from questionnaire import Questionnaire
q = Questionnaire(can_go_back=False)

def email(email):
    import re
    if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        return 'Enter a valid email'

def one(options):
    if len(options) < 1:
        return 'You must choose at least 1 type of junk mail'

def join(options):
    return ', '.join(options)

q.raw('email').validate(email)
q.many('junk_mail', 'this one weird trick', 'cheap viagra', 'dermatologists hate her').validate(one).transform(join)

q.run()
print(q.answers)
~~~

If a question has both a `transform` and `validate` function, validation is performed on the answer __before__ the transform is applied.


## Conditional Questions
One of __questionnaire__'s coolest features is including questions conditionally based on previous answers. The API for conditional questions is simple and flexible.

If you add questions with the same key to a questionnaire, the conditions assigned to the questions determine which one is presented to the user. __questionnaire__ iterates through the questions in the order they were added, __and presents the first question whose condition is satisfied, or whose condition is None__. If none of the questions for a key has a condition that is satisfied, all questions for this key are skipped.

A condition can be added to a question by chaining a call to `condition` onto the `one`, `many`, or `raw` call. A list of condition tuples must be passed. The first two values in a tuple, the __key__ and the __value__, are required. The third value, the __operator__, is optional (the default operator is `'=='`).

A __key__ is a key for a previously answered question in the questionnaire. The __key__ is used to look up the answer, and the answer gets compared with the __value__. If their relationship is true under the __operator__, this condition tuple is satisfied.

If all the condition tuples for a question are satisfied, the question's condition is satisfied.


### Condition Operators
The default operator is __equals__. The following operators can be passed as strings: `==`, `!=`, `<`, `>`, `<=`, `>=`, and their corresponding operator functions are looked up. If you want to define your own operators, make sure they are functions that accept two values (the values to be compared) and return a boolean.


## Questionnaire Options
These can be passed to a questionnaire when you instantiate it. You can also change these properties (they have the same names) directly on the questionnaire instance while it's running.

- `show_answers`: show all previous answers above question prompt
- `can_go_back`: allow users to go back


## Writing Your Own Prompters
__questionnaire__ is easy to extend. Write a prompter function that satisfies the prompter API. When you add a question to your questionnaire, instead of invoking `one`, `many`, or `raw`, invoke the generic `add` function, and pass a function as the `prompter` arg.

__The prompter API is super simple__: a prompter is a function that should display a question and capture user input. It returns this input as an `answer`.


### Going Back
If you want your prompter to allow users to go back, simply raise a `QuestionnaireGoBack` exception in the body of your prompter function instead of returning the answer. This exception can imported like so: `from questionnaire.prompters import QuestionnaireGoBack`. 

When you raise this exception in your prompter, you can pass the __number of steps to go back__ into the exception's constructor. For example, `raise QuestionnaireGoBack(2)` will go back two questions. If no value is passed to the constructor, the user goes back one question.


## Tests
If you've forked __questionnaire__ and want to make sure it's not broken, the modules in the `examples` directory should be used to test it. Run, for example, `python -m examples.plans_client` or `python -m examples.activities_client` from the root of the repo.


## Contributing
If you want to improve __questionnaire__, fork the repo and submit a pull request. Integration tests for the prompters would be nice. I think it would also be nice to refactor the raw prompter to use curses.


## Gotchas
__questionnaire__ merges `stdout` with `stderr` while the prompters are running. If you run a questionnaire and redirect `stderr` you'll find it contains everything printed to the terminal by `curses`.


## License
This code is licensed under the [MIT License](https://opensource.org/licenses/MIT).
