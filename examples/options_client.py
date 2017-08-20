from questionnaire import Questionnaire
q = Questionnaire()

q.many('options', 'Option 1', 'Option 2', prompt='Choose some options')
q.many('more', 'Option 3', 'Option 6', prompt='Choose some more')

q.run()
print(q.answers)

q.many('yet_more', 'Option 7', 'Option 8', prompt='And more...')
q.many('done', 'Option 9', 'Option 10', prompt='Last ones')

q.run()
print(q.answers)
