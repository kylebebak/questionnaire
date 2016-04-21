# questionnaire

__questionnaire__ is a Python library that uses [pick](https://github.com/wong2/pick) to prompt a user to answer a series of questions. At the end of the questionnaire if returns the answers as a dict.

As with __pick__, __questionnaire__ supports multiple choice questions only. However, __questionnaire__ allows users to select multiple options for a single question.

__questionnaire__'s most powerful feature is the ability to include any question conditionally based on previous answers. The API for conditional questions is simple and flexible.
  
Finally, users can use <kbd>&larr;</kbd> or <kbd>h</kbd> to go back in a questionnaire.

## Installation
```sh
pip install questionnaire
```

## Examples
Check out [this client](examples/client.py) that uses __questionnaire__ to build up a dict of answers for easy generating an `ansible-playbook` command for administering servers.

![questionnaire-client-ansible](https://raw.githubusercontent.com/kylebebak/questionnaire/master/examples/client.gif)

## Multiple options

## Conditional questions

## Tests


## LICENSE
This code is licensed under the [MIT License](https://opensource.org/licenses/MIT).
