from questionnaire import Questionnaire
q = Questionnaire()


def two(options):
    if len(options) < 2:
        return 'You must choose at least 2 options'


def join(options):
    return ', '.join(options)


q.many('options', 'Option 1', 'Option 2', 'Option 3', prompt='Choose some options').validate(two).transform(join)
q.many('more', 'Option 4', 'Option 5', 'Option 6', prompt='Choose some more').validate(two).transform(join)

q.run()
print(q.answers)


q.many('yet_more', 'Option 7', 'Option 8', prompt='And more...', default=[0, 1])
q.many('done', 'Option 9', 'Option 10', prompt='Last ones', default=1)

q.run()
print(q.answers)
