from questionnaire import Questionnaire
q = Questionnaire()

q.one('day', 'monday', 'friday', 'saturday')
q.one('time', 'morning', 'night')

q.many('activities', 'tacos de pastor', 'go to cantina', 'write code').condition(('time', 'night'))
q.many('activities', 'barbacoa', 'watch footy', 'walk dog').condition(('day', 'saturday'), ('time', 'morning'))
q.many('activities', 'eat granola', 'get dressed', 'go to work').condition(('time', 'morning'))

q.run()
print(q.format_answers(fmt='array'))
