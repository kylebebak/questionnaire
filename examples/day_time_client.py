from questionnaire import Questionnaire
q = Questionnaire()

q.one('day', 'monday', 'friday', 'saturday', prompt='What day is it?')
q.one('time', ('morning', 'in the morning'), ('night', 'at night'), prompt='What time is it?')

q.run()
print(q.format_answers())
