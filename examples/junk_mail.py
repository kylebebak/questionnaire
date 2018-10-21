from questionnaire import Questionnaire
q = Questionnaire(can_go_back=False)


def email(email):
    import re
    if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        return 'Enter a valid email'


def one(options):
    if len(options) < 1:
        return 'You must choose at least 1 type of junk mail'


def join(options):
    return ', '.join(options)


q.raw('email').validate(email)
q.many('junk_mail', 'this one weird trick', 'cheap viagra', 'dermatologists hate her').validate(one).transform(join)

q.run()
print(q.answers)
