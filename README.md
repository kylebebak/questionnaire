# questionnaire

__questionnaire__ is a Python package that to prompts users to answer a series of questions, and returns the answers as a `key -> answer` OrderedDict. __questionnaire__ allows users to go back and answer questions again. It works with Python 2 and 3.

## Installation
```sh
pip install questionnaire
```

## Usage
Instantiate a questionnaire and add some questions.
```py
from questionnaire import Questionnaire
q = Questionnaire()

q.add_question('day', options=['monday', 'friday', 'saturday'])
q.add_question('time', options=['morning', 'night'])
```

Add a group of conditional questions. Only one of these questions will be asked, depending on the answers to the first two questions.
```py
# nights
q.add_question('activities', prompter='multiple', options=['eat tacos de pastor', 'go to the cantina', 'do some programming']).\
    add_condition(keys=['time'], vals=['night'])
# saturday morning
q.add_question('activities', prompter='multiple', options=['eat barbacoa', 'watch footy', 'walk the dog']).\
    add_condition(keys=['day', 'time'], vals=['saturday', 'morning'])
# other mornings
q.add_question('activities', prompter='multiple', options=['eat granola', 'get dressed', 'go to work']).\
    add_condition(keys=['time'], vals=['morning'])
```

Run the questionnaire and print the answers.
```py
answers = q.run()
print(answers)
```

![](https://raw.githubusercontent.com/kylebebak/questionnaire/master/examples/activities_client.gif)

Here's an example that handles raw input. First, add a question using the `raw` prompter.
```py
from questionnaire import Questionnaire
q = Questionnaire()
q.add_question('age', prompter="raw", prompt='How old are you?', type=int)
```

Now you can ask users about their plans, based on how old they are.
```py
# youngsters (age <= 18)
q.add_question('plans', prompt="Where do you want to go to school?", options=['Valley College', 'La Escuela de Calor']).\
    add_condition(keys=['age'], vals=[18], operators=['<='])
q.add_question('plans', prompt="Where do you want to work?", options=['On a farm', 'In an office', 'On the couch']).\
    add_condition(keys=['age'], vals=[40], operators=['<='])
q.add_question('plans', prompt="Where do you want to vacation?", options=['El Caribe', 'On a cruise ship', 'Las Islas Canarias']).\
    add_condition(keys=['age'], vals=[60], operators=['<='])
# old folks (more than 60 years old)
q.add_question('plans', prompt="Where do you want to retire?", options=['El campo', 'The beach', 'San Miguel de Allende'])

answers = q.run()
print(answers)
```

![](https://raw.githubusercontent.com/kylebebak/questionnaire/master/examples/plans_client.gif)


## More Examples
Check out clients in the `examples` directory. The [ansible client](examples/ansible_client.py) generates an answers dict that you pass to another program to build up an `ansible-playbook` command for administering servers. I do this almost every day at my job!

## Prompters
The core prompters are currently `single`, `multiple`, and `raw`. `single` is the default prompter. All three are used in the usage examples above.

`single` and `multiple` depend on the excellent [pick](https://github.com/wong2/pick) package. `multiple` allows users to pick [multiple options](#multiple-options) for a single question, while `raw` handles [raw input](#raw-input) with basic type checking.

__questionnaire__ is easy to extend. Write a prompter function that satisfies the prompter API, and instead of passing a string to `add_question` to look up one of the core prompters, pass your prompter function. Check out the [core prompters](questionnaire/prompters.py) for examples on how to write prompter functions.

### Multiple Options
If you want to allow the user to pick multiple options for a single question, pass `prompter="multiple"` and a list of `options` to `add_question`. The `questionnaire` will add the chosen options to the `answers` dict as a list. As with the default `single` prompter, users can use <kbd>&larr;</kbd> or <kbd>h</kbd> to go back.

### Raw Input
For raw input, pass `prompter="raw"` and a `type` (`str`, `int`, `float`, ...) to `add_question`. The default type is `str`. By default, the user can go back by entering `<`. To change this, pass your own `go_back` string to `add_question`.


## Conditional Questions
__questionnaire__'s coolest feature is including questions conditionally based on previous answers. The API for conditional questions is simple and flexible.

If you add questions with the same key to a questionnaire, the conditions assigned to the questions determine which one is presented to the user. __questionnaire__ iterates through the questions in the order they were added, __and presents the first question whose condition is satisfied, or whose condition is None__. If none of the questions for a key has a condition that is satisfied, then all questions for this key are skipped.

A condition can be added to a question by chaining a call to `add_condition` onto the `add_question` call. The args `keys` and `vals`, and [optionally operators](#condition-operators), must be passed to `add_condition`. These keywords arguments must point to lists or iterables that have the same length.

Each item in the `keys` list must be a key for a previously answered question in the questionnaire. In a condition, the __answers__ get compared with __vals__, and if their relationships are all `True` under the __operators__, the condition is satisfied. If this sounds tricky, just check out the clients!

#### Condition Operators
The default operator is __equals__. The following operators can be passed as strings: `==`, `!=`, `<`, `>`, `<=`, `>=`, and their corresponding operator functions are looked up. If you want to define your own operators, make sure they are functions that accept two values and return a boolean. Hint: use lambda functions.

## Tests
Not yet...

## Contributing
If you want to improve __questionnaire__ with tests, new core prompters, or other features, fork the repo and submit a pull request!

## License
This code is licensed under the [MIT License](https://opensource.org/licenses/MIT).
