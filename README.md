# questionnaire

__questionnaire__ is a Python library that uses prompters to prompt a user to answer a series of questions. At the end of the questionnaire it returns the answers as a `key -> answer` OrderedDict. All of __questionnaire__'s prompters allow users to go back to answer questions again. __questionnaire__ works with Python 2 and 3.

The core prompters are `single`, `multiple`, and `raw`. The first two depend on the excellent [pick](https://github.com/wong2/pick) package. `multiple` allows users to pick [multiple options](#multiple-options) for a single question, while `raw` handles [raw input](#raw-input) with basic type checking.

__questionnaire__ is extensible via writing new prompters that satisfy a simple API. Writing prompters is easy. Check out the [prompters module](questionnaire/prompters.py) for details on how to do so.

__questionnaire__'s most powerful feature is the ability to include any question conditionally based on previous answers. The API for [conditional questions](#conditional-questions) is simple and flexible.

## Installation
```sh
pip install questionnaire
```

## Examples
Check out clients in the `examples` directory. One uses __questionnaire__ to build up a dict of answers for generating an `ansible-playbook` command for administering servers. These examples cover most of __questionnaire__'s API, and provide a good example of how to implement [conditional questions](#conditional-questions).

![questionnaire-client-ansible](https://raw.githubusercontent.com/kylebebak/questionnaire/master/examples/client.gif)

## Basic Usage
Instantiate a `questionnaire`, add some questions with `add_question` (optionally chaining conditions onto the questions with `add_condition`), and call `run`. `add_question` requires only one parameter: `key`. If you wish to use something other than the default `prompter` with the default `prompt`, pass in these args as well. The rest of the args must be keyword arguments, that will be passed to whatever prompter is used by the question.

~~~py
from questionnaire import Questionnaire
q = Questionnaire()

q.add_question('day', options=['monday', 'friday', 'saturday'])
q.add_question('time', options=['morning', 'evening', 'night'])

# saturday morning
q.add_question('todo', prompter="multiple", options=['eat barbacoa', 'eat pozole']).\
    add_condition(keys=['day', 'time'], vals=['saturday', 'morning'])
# other mornings
q.add_question('todo', prompter="multiple", options=['get dressed', 'walk the dog', 'go to work']).\
    add_condition(keys=['time'], vals=['morning'])
# friday or saturday, evening or night
q.add_question('todo', prompter="multiple", options=['eat tostadas', 'go to the cantina']).\
    add_condition(keys=['day', 'time'], vals=[('friday', 'saturday'), ('evening', 'night')], operators=[lambda x, y: x in y]*2)
# monday night is skipped

q.add_question('age', 'how old are you?', prompter="raw", type="int")

choices = q.run()
~~~

## Multiple Options
If you want to allow the user to pick multiple options for a single question, pass `prompter="multiple"` and a list of `options` to `add_question`. The `questionnaire` will add a list of the chosen options to the `answers` dict. As with the default `single` prompter, users can use <kbd>&larr;</kbd> or <kbd>h</kbd> to go back.

## Raw Input
For raw input, pass `prompter="raw"` and a `type` (`str`, `int`, `float`, ...) to `add_question`. The default type is `str`. By default, the user can go back by entering `<`. To change this, pass your own `go_back` string to `add_question`.

## Conditional Questions
If you add questions with the same key to a questionnaire, the conditions assigned to the questions will determine which one is presented to the user. __questionnaire__ will iterate through the questions in the order in which they were added, __and will present the first question whose condition is satisfied, or whose condition is None__. If none of the questions for a key has a condition that is satisfied, then all questions for this key are skipped.

A condition can be added to a question by chaining a call to `add_condition` onto the `add_question` call. The args `keys` and `vals`, and [optionally operators](#condition-operators), must be passed to `add_condition`. These keywords arguments must point to lists or iterables that have the same length.

Each item in the `keys` list must be a key for a previously answered question in the questionnaire. In a condition, the __answers__ get compared with __vals__, and if their relationships are all `True` under the __operators__, the condition is satisfied. This might sound tricky, but it's surprisingly flexible and simple. If in doubt just check out the clients!

### Condition Operators
The default operator is __equals__. The following operators can be passed as strings: `==`, `!=`, `<`, `>`, `<=`, `>=`, and their corresponding operator functions will be looked up. If you want to define your own operators, make sure they are functions that accept two values and return a boolean. Hint: use lambda functions.

## Tests
Not yet...

## Extending
If you want to improve __questionnaire__ with tests or new prompters or other features, fork the repo and submit a pull request!

## License
This code is licensed under the [MIT License](https://opensource.org/licenses/MIT).
