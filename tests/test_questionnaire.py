"""Usage: from repo root, run `python -m unittest discover tests -v`
"""
import unittest
from random import randrange

from questionnaire import Questionnaire
from questionnaire.prompters import QuestionnaireGoBack


class TestQuestionnaire(unittest.TestCase):
    def test_questionnaire(self):
        q = Questionnaire()
        q.add('k', prompter=lambda prompt: 'v')
        q.run()
        self.assertEqual(q.answers['k'], 'v')

        q.add('k2', prompter=lambda prompt: 'v2_first').condition(('k', 'v_'))
        q.add('k2', prompter=lambda prompt: 'v2_second').condition(('k', 'v'))
        q.ask()
        self.assertEqual(q.answers['k2'], 'v2_second')
        self.assertEqual(len(q.answers), 2)

        q.add('k3', prompter=lambda prompt: randrange(10)).validate(
            lambda a: None if a == 0 else 'error'
        ).transform(lambda a: a-1)
        q.ask()
        self.assertEqual(q.answers['k3'], -1)

        q.reset()
        self.assertEqual(dict(q.answers), {})

    def test_format_answers(self):
        q = Questionnaire()
        q.add('k', prompter=lambda prompt: 'v')
        q.run()
        self.assertEqual(q.format_answers(fmt='obj'), '{"k": "v"}')
        self.assertEqual(q.format_answers(fmt='array'), '[["k", "v"]]')
        self.assertEqual(q.format_answers(fmt='plain'), 'k: v')

    def test_go_back_remove(self):
        def go_back(prompt):
            raise QuestionnaireGoBack(2)

        q = Questionnaire()
        q.add('k', prompter=lambda prompt: 'v')
        q.ask()
        self.assertEqual(q.answers['k'], 'v')

        q.add('k2', prompter=lambda prompt: 'v2')
        q.ask()
        self.assertEqual(q.answers['k2'], 'v2')

        q.go_back(1)
        self.assertEqual(q.answers['k'], 'v')
        self.assertEqual(q.answers.get('k2'), None)
        q.ask()
        self.assertEqual(q.answers['k2'], 'v2')

        q.add('k3', prompter=go_back)
        q.ask()
        self.assertEqual(len(q.answers), 0)

        q.remove('k2')
        q.remove('k3')
        q.run()
        self.assertEqual(dict(q.answers), {'k': 'v'})


if __name__ == '__main__':
    unittest.main()
