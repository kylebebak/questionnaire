from questionnaire import Questionnaire
q = Questionnaire()

q.many('options', 'Option 1', 'Option 2', prompt='Choose some options')
q.many('more', 'Option 3', 'Option 4', prompt='Choose some more')

q.run()
print(q.answers)

q.many('yet_more', 'Option 5', 'Option 6', prompt='And more...')
q.many('done', 'Option 7', 'Option 8', prompt='Last ones')

q.run()
print(q.answers)
