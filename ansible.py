#-*-coding:utf-8-*-

from questionnaire import Question, Questionnaire

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
q.add_question(Question('env', ENVS))
# kind
q.add_question(Question('kind', KINDS))
# playbook
q.add_question(Question('playbook', DEPLOY_PLAYBOOKS,
    condition={'keys': ['kind'], 'vals': ['deploy']}))
q.add_question(Question('playbook', SERVICE_PLAYBOOKS,
    condition={'keys': ['kind'], 'vals': ['service']}))
# tags
q.add_question(Question('tags', DEPLOY_PLAYBOOK_TAGS, multiple=True,
    condition={'keys': ['kind', 'playbook'], 'vals': ['deploy', 'deploy']}))
q.add_question(Question('tags', DEPLOY_ROLE_TAGS, multiple=True,
    condition={'keys': ['kind'], 'vals': ['deploy']}))
q.add_question(Question('tags', SERVICE_PLAYBOOK_TAGS, multiple=True,
    condition={'keys': ['kind', 'playbook'], 'vals': ['service', 'service']}))
q.add_question(Question('tags', [], multiple=True,
    condition={'keys': ['kind'], 'vals': ['service']}))
# action
q.add_question(Question('action', SERVICE_ACTIONS,
    condition={'keys': ['kind'], 'vals': ['service']}))
# services
q.add_question(Question('services', [], multiple=True,
    condition={'keys': ['kind', 'playbook'], 'vals': ['service', 'service']}))
q.add_question(Question('services', SERVICES_DEV, multiple=True,
    condition={'keys': ['kind', 'env'], 'vals': ['service', 'development']}))
q.add_question(Question('services', SERVICES_STG, multiple=True,
    condition={'keys': ['kind', 'env'], 'vals': ['service', 'staging']}))
q.add_question(Question('services', SERVICES_PRD, multiple=True,
    condition={'keys': ['kind', 'env'], 'vals': ['service', 'production']}))

choices = q.run()
print(choices)
