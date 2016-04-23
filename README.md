# questionnaire

__questionnaire__ is a Python library that uses [pick](https://github.com/wong2/pick) to prompt a user to answer a series of questions. At the end of the questionnaire if returns the answers as a `key -> option(s)` dict.

__questionnaire__ supports multiple choice questions only, but it allows allows users to pick [multiple options](#multiple-options) for a single question.

__questionnaire__'s most powerful feature is the ability to include any question conditionally based on previous answers. The API for [conditional questions](#conditional-questions) is simple and flexible.
  
Finally, users can use <kbd>&larr;</kbd> or <kbd>h</kbd> to go back in a questionnaire.

## Installation
```sh
pip install questionnaire
```

## Examples
Check out clients in the `examples` directory. One uses __questionnaire__ to build up a dict of answers for generating an `ansible-playbook` command for administering servers. These examples cover most of __questionnaire__'s API, and provide a good example of how to implement [conditional questions](#conditional-questions).

![questionnaire-client-ansible](https://raw.githubusercontent.com/kylebebak/questionnaire/master/examples/client.gif)

## Basic Usage
Instantiate a `questionnaire`, add some questions with `add_question` (optionally chaining conditions onto the questions with `add_condition`), and call `run`. Add question requires only one parameter: `key`. If you wish to use something other than the default `prompter` with the default `prompt`, pass in these args as well. The rest of the args must be keyword arguments, that will be passed to whatever prompter is used by the question.

~~~py
from questionnaire import Questionnaire
q = Questionnaire()

q.add_question('day', options=['monday', 'friday', 'saturday'])
q.add_question('time', options=['morning', 'evening', 'night'])

# saturday morning
q.add_question('todo', prompter="multiple", options=['eat barbacoa', 'eat pozole']). \
    add_condition(keys=['day', 'time'], vals=['saturday', 'morning'])
# other mornings
q.add_question('todo', prompter="multiple", options=['get dressed', 'walk the dog', 'go to work']). \
    add_condition(keys=['time'], vals=['morning'])
# friday or saturday, evening or night
q.add_question('todo', prompter="multiple", options=['eat tostadas', 'go to the cantina']). \
    add_condition(keys=['day', 'time'], vals=[('friday', 'saturday'), ('evening', 'night')], operators=[lambda x, y: x in y]*2)
# monday night is skipped

q.add_question('age', 'how old are you?', prompter="raw", type="int")

choices = q.run()
~~~

## Multiple Options
If you want to allow the user to pick multiple options for a single question, pass prompter=`multiple` to `add_question`. The `questionnaire` will assign a list of the chosen options to the key.

## Conditional Questions
If you add questions with the same key to a questionnaire, the conditions assigned to the questions will determine which one is presented to the user. __questionnaire__ will iterate through the questions in the order in which they were added, __and will present the first question for which the condition is satisfied, or for which there is no condition__. If none of the questions for a key has a condition that is satisfied, then all questions for this key are skipped.

A condition can be added to a question by chaining a call to `add_condition` onto the `add_question` call. The args `keys` and `vals`, and optionally `operators`, must be passed to `add_condition`. These keywords arguments must point to lists or iterables that have the same length. __\*\*__

Each item in the `keys` list must be a key for a previously answered question in the questionnaire. In a condition, the __answers__ get compared with __vals__, and if their relationships are all `True` under the __operators__, the condition is satisfied. This might sound tricky, but it's surprisingly flexible and simple. If in doubt, seriously, check out the clients!

__\*\*__ The default operator is __equals__. The following operators can be passed as strings: `==`, `!=`, `<`, `>`, `<=`, `>=`. If you want to define your own operators, make sure they are functions that accept two values and return a boolean. Hint: use lambda functions.

## Tests
Not yet...

## Extending and Forks

## License
This code is licensed under the [MIT License](https://opensource.org/licenses/MIT).
