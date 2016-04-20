"""A sample client for questionnaire. It builds a dict of values that can
be passed to another program to build a valid `ansible-playbook` command.
"""
from questionnaire import Questionnaire

# env
ENVS = ['development', 'staging', 'production']
# kind
KINDS = ['deploy', 'service']
# playbook
DEPLOY_PLAYBOOKS = ['deploy', 'backend', 'create_user', 'database', 'message', 'webserver']
SERVICE_PLAYBOOKS = ['service', 'backend', 'database', 'message', 'webserver']
# tags
DEPLOY_PLAYBOOK_TAGS = ['backend', 'create_user', 'database', 'message', 'webserver']
DEPLOY_ROLE_TAGS = ['clone_repo', 'createsuperuser', 'django', 'env_vars', 'fixtures', 'iptables', 'logrotate',
    'migrate', 'nginx', 'node', 'postgresql', 'redis', 'upstart', 'vagrant', 'virtualenv']
SERVICE_PLAYBOOK_TAGS = ['backend', 'database', 'message', 'webserver']
# action
SERVICE_ACTIONS = ['started', 'stopped', 'restarted', 'reloaded']
# services
SERVICES_INITD = ['redis_6379', 'postgresql', 'nginx', 'firewall']
SERVICES_UPSTART = ['gunicorn', 'celery-worker', 'celery-beat', 'celery-flower']
SERVICES_DEV = SERVICES_INITD + [s + "-development" for s in SERVICES_UPSTART]
SERVICES_STG = SERVICES_INITD + [s + "-staging" for s in SERVICES_UPSTART]
SERVICES_PRD = SERVICES_INITD + [s + "-production" for s in SERVICES_UPSTART]

q = Questionnaire()

# env
q.add_question('env', ENVS)
# kind
q.add_question('kind', KINDS)
# playbook
q.add_question('playbook', DEPLOY_PLAYBOOKS,
    condition={'keys': ['kind'], 'vals': ['deploy']})
q.add_question('playbook', SERVICE_PLAYBOOKS,
    condition={'keys': ['kind'], 'vals': ['service']})
# tags
q.add_question('tags', DEPLOY_PLAYBOOK_TAGS, multiple=True,
    condition={'keys': ['kind', 'playbook'], 'vals': ['deploy', 'deploy']})
q.add_question('tags', DEPLOY_ROLE_TAGS, multiple=True,
    condition={'keys': ['kind'], 'vals': ['deploy']})
q.add_question('tags', SERVICE_PLAYBOOK_TAGS, multiple=True,
    condition={'keys': ['kind', 'playbook'], 'vals': ['service', 'service']})
q.add_question('tags', [], multiple=True,
    condition={'keys': ['kind'], 'vals': ['service']})
# action
q.add_question('action', SERVICE_ACTIONS,
    condition={'keys': ['kind'], 'vals': ['service']})
# services
q.add_question('services', [], multiple=True,
    condition={'keys': ['kind', 'playbook'], 'vals': ['service', 'service']})
q.add_question('services', SERVICES_DEV, multiple=True,
    condition={'keys': ['kind', 'env'], 'vals': ['service', 'development']})
q.add_question('services', SERVICES_STG, multiple=True,
    condition={'keys': ['kind', 'env'], 'vals': ['service', 'staging']})
q.add_question('services', SERVICES_PRD, multiple=True,
    condition={'keys': ['kind', 'env'], 'vals': ['service', 'production']})

choices = q.run()
print(choices)
