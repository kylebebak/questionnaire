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
