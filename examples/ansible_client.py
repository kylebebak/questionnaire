"""A sample client for questionnaire. It builds a dict of values that can
be passed to another program to build a valid `ansible-playbook` command.
"""
from questionnaire import Questionnaire

SERVICES_INITD = ['redis_6379', 'postgresql', 'nginx', 'firewall']
SERVICES_UPSTART = ['gunicorn', 'celery-worker', 'celery-beat', 'celery-flower']
SERVICES_DEV = SERVICES_INITD + [s + "-development" for s in SERVICES_UPSTART]
SERVICES_STG = SERVICES_INITD + [s + "-staging" for s in SERVICES_UPSTART]
SERVICES_PRD = SERVICES_INITD + [s + "-production" for s in SERVICES_UPSTART]

q = Questionnaire()

# ENV
q.add_question('env', options=['development', 'staging', 'production'])

# KIND
q.add_question('kind', options=['deploy', 'service'])

# PLAYBOOK
q.add_question('playbook', options=['deploy', 'backend', 'create_user', 'database', 'message', 'webserver']).\
    add_condition(keys=['kind'], vals=['deploy'])

q.add_question('playbook', options=['service', 'backend', 'database', 'message', 'webserver']).\
    add_condition(keys=['kind'], vals=['service'])

# TAGS
q.add_question('tags', prompter="multiple", options=['backend', 'create_user', 'database', 'message', 'webserver']).\
    add_condition(keys=['kind', 'playbook'], vals=['deploy', 'deploy'])

q.add_question('tags', prompter="multiple",
    options=['clone_repo', 'createsuperuser', 'django', 'env_vars', 'fixtures',
             'iptables', 'logrotate', 'migrate', 'nginx', 'node', 'postgresql',
             'redis', 'upstart', 'vagrant', 'virtualenv']).\
    add_condition(keys=['kind'], vals=['deploy'])

q.add_question('tags', prompter="multiple", options=['backend', 'database', 'message', 'webserver']).\
    add_condition(keys=['kind', 'playbook'], vals=['service', 'service'])

q.add_question('tags', prompter="multiple", options=[]).\
    add_condition(keys=['kind'], vals=['service'])

# BRANCH
q.add_question('branch', prompter="raw").add_condition(keys=['kind'], vals=['deploy'])

# ACTION
q.add_question('action', options=['started', 'stopped', 'restarted', 'reloaded']).\
    add_condition(keys=['kind'], vals=['service'])

# SERVICES
q.add_question('services', prompter="multiple", options=[]).\
    add_condition(keys=['kind', 'playbook'], vals=['service', 'service'])

q.add_question('services', prompter="multiple", options=SERVICES_DEV).\
    add_condition(keys=['kind', 'env'], vals=['service', 'development'])
q.add_question('services', prompter="multiple", options=SERVICES_STG).\
    add_condition(keys=['kind', 'env'], vals=['service', 'staging'])
q.add_question('services', prompter="multiple", options=SERVICES_PRD).\
    add_condition(keys=['kind', 'env'], vals=['service', 'production'])

answers = q.run()
print(answers)
