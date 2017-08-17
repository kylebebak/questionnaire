import sys

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
