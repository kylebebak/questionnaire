# questionnaire

![License](https://camo.githubusercontent.com/890acbdcb87868b382af9a4b1fac507b9659d9bf/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f6c6963656e73652d4d49542d626c75652e737667)

__questionnaire__ is a mini-DSL for writing command line questionnaires. It prompts a user to answer a series of questions and returns the answers.

__questionnaire__ is simple and powerful. Some features: 

- Prints the answers as JSON to stdout
  + You can pipe the answers of a questionnaire to any program that can parse JSON
- Allows users to go back and reanswer questions
- Supports conditional questions (questions can depend on previous answers)
- Supports the following types of questions: raw input, choose one, choose many
- No mandatory coupling between question presentation and answer values


## Installation
__questionnaire__ is written in Python. The best way to install it is with `pip`.

```sh
pip install questionnaire
```


## Usage
Paste the following into a file and save it. Let's assume you save it as `questions.py`. Now go the command line and run `python questions.py`.

```py
# questions.py
from questionnaire import Questionnaire
q = Questionnaire()

q.add_question('day', prompt='What day is it?', options=['monday', 'friday', 'saturday'])
q.add_question('time', prompt='What time is it?', options=['morning', 'night'],
               verbose_options=['in the morning', 'at night'])

answers = q.run()
```

What's happening here? We instantiate a questionnaire with `q = Questionnaire()`, add two questions to it, and run the questionnaire. At the end the answers are dumped to stdout as JSON.

See those optional `verbose_options`? The presentation of your questionnaire can be totally decoupled from the answers it returns!

Now try running `python questions.py > questions_output.json`. Check out the answers in the output file. You could have just as easily piped these to another program, and all it would have to do to handle the answers is parse that JSON.


### Getting Fancy
Add a group of conditional questions to the questionnaire above. Only one of these questions will be asked, depending on the answers to the first two questions. Run the questionnaire with `python questions.py`, and inspect the answers as well.

```py
# questions.py
from questionnaire import Questionnaire
q = Questionnaire(dump_to_array=True)

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

answers = q.run()
print()
for q, a in answers.items():
    print(q, a)
```

As you can see, the answers are always printed to stdout as JSON, but they're also returned  as an ordered dictionary (a Python `OrderedDict` to be exact).

What does this mean? If you don't want to write Python code, you can write a standalone questionnaire that just pipes its answers to another program for handling. If you want to handle them in the same script, you get back a nice `OrderedDict` with all the answers!

Also, did you notice the `dump_to_array=True` argument? This prints the answers as a JSON array instead of a JSON object. This guarantees parsing the answers doesn't screw up their order, although it might make parsing more cumbersome.

![](https://raw.githubusercontent.com/kylebebak/questionnaire/master/examples/activities_client.gif)

- - -

Here's another example. This one handles raw input. First, add a question using the `raw` prompter.
```py
from questionnaire import Questionnaire
q = Questionnaire()
q.add_question('age', prompter="raw", prompt='How old are you?', type=int)
```

Now you can ask users about their plans for the future, based on how old they are.
```py
# youngsters (age <= 18)
q.add_question('plans', prompt="Where do you want to go to school?",
    options=['Valley College', 'La Escuela de Calor']).\
    add_condition(keys=['age'], vals=[18], operators=['<='])
q.add_question('plans', prompt="Where do you want to work?",
    options=['On a farm', 'In an office', 'On the couch']).\
    add_condition(keys=['age'], vals=[40], operators=['<='])
q.add_question('plans', prompt="Where do you want to vacation?",
    options=['El Caribe', 'On a cruise ship', 'Las Islas Canarias']).\
    add_condition(keys=['age'], vals=[60], operators=['<='])
# old folks (more than 60 years old)
q.add_question('plans', prompt="Where do you want to retire?",
    options=['El campo', 'The beach', 'San Miguel de Allende'])

answers = q.run()
```

![](https://raw.githubusercontent.com/kylebebak/questionnaire/master/examples/plans_client.gif)


## 
## More Examples
Check out clients in the `examples` directory. The [Ansible client](examples/ansible_client.py) generates an answers dict that you pass to another program to build up an `ansible-playbook` command for administering servers. I do this almost every day at my job!


## Prompters
The core prompters are currently `single`, `multiple`, and `raw`. The first two depend on the excellent [pick](https://github.com/wong2/pick) package. All three are used in the usage examples above.

`single` is the default prompter. It requires the user to pick one of the options from the options list. `multiple` allows users to pick [multiple options](#multiple-options) for a single question, while `raw` handles [raw input](#raw-input) with basic type checking.

__questionnaire__ is easy to extend. Write a prompter function that satisfies the prompter API, and instead of passing a string to `add_question` to look up one of the core prompters, pass your prompter function. Check out the [core prompters](questionnaire/prompters.py) for examples on how to write prompter functions.


### Multiple Options
If you want to allow the user to pick multiple options for a single question, pass `prompter="multiple"` and a list of `options` to `add_question`. The `questionnaire` will add the chosen options to the `answers` dict as a list. As with the default `single` prompter, users can use <kbd>&larr;</kbd> or <kbd>h</kbd> to go back.


### Raw Input
For raw input, pass `prompter="raw"` and a `type` (`str`, `int`, `float`, ...) to `add_question`. The default type is `str`. By default, the user can go back from a raw input question by entering `<` as the answer. To change this, pass your own `go_back` string to `add_question`.


## Conditional Questions
__questionnaire__'s coolest feature is including questions conditionally based on previous answers. The API for conditional questions is simple and flexible.

If you add questions with the same key to a questionnaire, the conditions assigned to the questions determine which one is presented to the user. __questionnaire__ iterates through the questions in the order they were added, __and presents the first question whose condition is satisfied, or whose condition is None__. If none of the questions for a key has a condition that is satisfied, then all questions for this key are skipped.

A condition can be added to a question by chaining a call to `add_condition` onto the `add_question` call. The args `keys` and `vals`, and [optionally operators](#condition-operators), must be passed to `add_condition`. These keywords arguments must point to lists or iterables that have the same length.

Each item in the `keys` list must be a key for a previously answered question in the questionnaire. In a condition, the __answers__ get compared with __vals__, and if their relationships are all `True` under the __operators__, the condition is satisfied. If this sounds tricky, just check out the clients!


### Condition Operators
The default operator is __equals__. The following operators can be passed as strings: `==`, `!=`, `<`, `>`, `<=`, `>=`, and their corresponding operator functions are looked up. If you want to define your own operators, make sure they are functions that accept two values and return a boolean. Hint: use lambda functions.


## Tests
If you've forked __questionnaire__ and want to make sure it's not broken, the modules in the `examples` directory should be used to test it. Run, for example, `python -m examples.plans_client` or `python -m examples.activities_client` from the root of the repo.


## Contributing
If you want to improve __questionnaire__ with tests, new core prompters, or other features, fork the repo and submit a pull request. Automated tests or new prompters would be nice!


## Gotchas
__questionnaire__ merges `stdout` with `stderr` while the prompters are running. If you run a questionnaire and redirect `stderr` you'll find it contains everything printed to the terminal by `curses`.


## License
This code is licensed under the [MIT License](https://opensource.org/licenses/MIT).
