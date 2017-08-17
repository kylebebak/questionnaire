# questionnaire

![License](https://camo.githubusercontent.com/890acbdcb87868b382af9a4b1fac507b9659d9bf/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f6c6963656e73652d4d49542d626c75652e737667)

__questionnaire__ is a mini-DSL for writing command line questionnaires. It prompts a user to answer a series of questions and returns the answers.

__questionnaire__ is simple and powerful. Some features: 

- Print answers as JSON or as plain text to stdout
  + Pipe answers to other programs and parse them easily
- Allow users to reanswer questions
- Run all remaining questions or ask them one at a time
  + [Extend questionnaire as it's being run](#github-api)
- Conditional questions can depend on previous answers
- __choose one__, __choose many__, and __raw input__ questions
- Transform and validate answers
- Question display decoupled from answer values
- Extend questionnaire by writing your own prompter


## Installation
__questionnaire__ is written in Python. The best way to install it is with `pip`.

~~~sh
pip install questionnaire
~~~


## Usage
Paste the following into a file and save it. Let's assume you save it as `questions.py`. Now go the command line and run `python questions.py`.

~~~py
# questions.py
from questionnaire import Questionnaire
q = Questionnaire()

q.add_question('day', prompt='What day is it?', options=['monday', 'friday', 'saturday'])
q.add_question('time', prompt='What time is it?', options=['morning', 'night'],
               verbose_options=['in the morning', 'at night'])

q.run()
print(q.format_answers())
~~~

What's happening here? We instantiate a questionnaire with `q = Questionnaire()`, add two questions to it, and run the questionnaire. At the end the answers are dumped to stdout as JSON.

See those optional `verbose_options`? The presentation of your questionnaire __can be decoupled from the answers it returns__.


### Getting Fancy
Add a group of conditional questions to the questionnaire above. Only one of these questions will be asked, depending on the answers to the first two questions. Run the questionnaire with `python questions.py`, and inspect the answers as well.

~~~py
# questions.py
from questionnaire import Questionnaire
q = Questionnaire()

q.add_question('day', options=['monday', 'friday', 'saturday'])
q.add_question('time', options=['morning', 'night'])

# nights
q.add_question('activities', prompter='multiple',
    options=['eat tacos de pastor', 'go to the cantina', 'do some programming']).\
    add_condition(keys=['time'], vals=['night'])
# saturday morning
q.add_question('activities', prompter='multiple',
    options=['barbacoa', 'footy', 'walk_dog'],
    verbose_options=['eat barbacoa', 'watch footy', 'walk the dog']).\
    add_condition(keys=['day', 'time'], vals=['saturday', 'morning'])
# other mornings
q.add_question('activities', prompter='multiple',
    options=['eat granola', 'get dressed', 'go to work']).\
    add_condition(keys=['time'], vals=['morning'])

q.run()
print(q.format_answers(fmt='array'))
~~~

As you can see, it's easy to print answers to stdout. What does this mean? If you don't want to write Python code, you can write a standalone questionnaire that just pipes its answers to another program for handling. If you want to handle them in the same script, just reference `q.answers`, which is a nice `OrderedDict`.

Also, did you notice the `fmt='array'` argument? This formats the answers as a JSON array instead of a JSON object. This guarantees parsing the answers doesn't screw up their order, although it might make parsing more cumbersome.


#### Plain Text
If you plan on piping the results of a questionnaire to a shell script, you might want plain text instead of JSON. Just pass `fmt='plain'` when you format the answers to your `Questionnaire`. The answers will be returned as plain text, one answer per line.

![](https://raw.githubusercontent.com/kylebebak/questionnaire/master/examples/activities_client.gif)


### GitHub API
Here's another example. This one handles raw input. It first prompts the user for their GitHub __username__ and __password__. It then pauses the questionnaire and uses these credentials to hit the GitHub API to get a list of all their repos. It then adds another question to the questionnaire and resumes it, prompting the user to choose one of these repos.

It depends on the `requests` library, so install it if you want to give it a try. First, add a question using the `raw` prompter.

~~~py
from questionnaire import Questionnaire
import requests

q = Questionnaire(show_answers=False, can_go_back=False)
q.add_question('user', prompter="raw", prompt='Username:', type=str)
q.add_question('pass', prompter="raw", prompt='Password:', type=str, secret=True)

q.run()
r = requests.get('https://api.github.com/user/repos',
                 auth=(q.answers.get('user'), q.answers.get('pass')))
if not(r.ok):
    print('username/password incorrect')
    sys.exit()

repos = [repo.get('url') for repo in r.json()]
q.add_question('repo', prompt="Choose a repo", options=repos)
q.run()
print(q.answers.get('repo'))

~~~


## More Examples
Check out clients in the `examples` directory. The [Ansible client](examples/ansible_client.py) generates an answers dict that you pass to another program to build up an `ansible-playbook` command for administering servers. I do this almost every day at my job!


## Prompters
The core prompters are currently `single`, `multiple`, `raw`. The first two depend on the excellent [pick](https://github.com/wong2/pick) package. All three are used in the usage examples above.

`single` is the default prompter. It requires the user to pick one of the options from the options list. `multiple` allows users to pick [multiple options](#multiple-options) for a single question, while `raw` handles [raw input](#raw-input) with basic type checking.


### Multiple Options
If you want to allow the user to pick multiple options for a single question, pass `prompter='multiple'` and a list of `options` to `add_question`. The `questionnaire` will add the chosen options to the `answers` dict as a list. As with the default `single` prompter, users can use <kbd>&larr;</kbd> or <kbd>h</kbd> to go back.


### Raw Input
For raw input, pass `prompter='raw'` and a `type` (`str`, `int`, `float`, ...) to `add_question`. The default type is `str`. By default, the user can go back from a raw input question by entering `<` as the answer. To change this, pass your own `go_back` string to `add_question`.

If you want to capture password input, or any other secret input, pass the `secret=True` arg to `add_question`.


## Conditional Questions
__questionnaire__'s coolest feature is including questions conditionally based on previous answers. The API for conditional questions is simple and flexible.

If you add questions with the same key to a questionnaire, the conditions assigned to the questions determine which one is presented to the user. __questionnaire__ iterates through the questions in the order they were added, __and presents the first question whose condition is satisfied, or whose condition is None__. If none of the questions for a key has a condition that is satisfied, then all questions for this key are skipped.

A condition can be added to a question by chaining a call to `add_condition` onto the `add_question` call. The args `keys` and `vals`, and [optionally operators](#condition-operators), must be passed to `add_condition`. These keywords arguments must point to lists or iterables that have the same length.

Each item in the `keys` list must be a key for a previously answered question in the questionnaire. In a condition, the __answers__ get compared with __vals__, and if their relationships are all `True` under the __operators__, the condition is satisfied. If this sounds tricky, just check out the clients!


### Condition Operators
The default operator is __equals__. The following operators can be passed as strings: `==`, `!=`, `<`, `>`, `<=`, `>=`, and their corresponding operator functions are looked up. If you want to define your own operators, make sure they are functions that accept two values and return a boolean.


## Questionnaire Options
Passed to a questionnaire when you instantiate it. You can also change these properties directly on the questionnaire instance while it's running.

- `show_answers`: show all previous answers above question prompt
- `can_go_back`: allow users to go back


## Writing Your Own Prompters
__questionnaire__ is easy to extend. Write a prompter function that satisfies the prompter API. When you add a question to your questionnaire, instead of passing a string to `add_question` to look up one of the core prompters, pass your prompter function.

__The prompter API is super simple__: a prompter is a function that should display a question and capture user input. It returns this input as an `answer`.


### Going Back
If you want your prompter to allow users to go back, simply raise a `QuestionnaireGoBack` exception in the body of your prompter function instead of returning the answer. This exception can imported like so: `from questionnaire.prompters import QuestionnaireGoBack`. 

When you raise this exception in your prompter, you can pass the __number of steps to go back__ into the exception's constructor. For example, `raise QuestionnaireGoBack(2)` will go back two questions. If no value is passed to the constructor, the user goes back one question.


## Tests
If you've forked __questionnaire__ and want to make sure it's not broken, the modules in the `examples` directory should be used to test it. Run, for example, `python -m examples.plans_client` or `python -m examples.activities_client` from the root of the repo.


## Contributing
If you want to improve __questionnaire__ with tests, new core prompters, or other features, fork the repo and submit a pull request. Automated tests or new prompters would be nice!


## Gotchas
__questionnaire__ merges `stdout` with `stderr` while the prompters are running. If you run a questionnaire and redirect `stderr` you'll find it contains everything printed to the terminal by `curses`.


## License
This code is licensed under the [MIT License](https://opensource.org/licenses/MIT).
