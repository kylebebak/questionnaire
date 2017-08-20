from questionnaire import Questionnaire
q = Questionnaire()

q.one('day', 'monday', 'friday', 'saturday')
q.one('time', 'morning', 'night')

q.many('activities', 'eat tacos de pastor', 'go to the cantina', 'do some programming').condition(('time', 'night'))
q.many('activities', 'eat barbacoa', 'watch footy', 'walk the dog').condition(('day', 'saturday'), ('time', 'morning'))
q.many('activities', 'eat granola', 'get dressed', 'go to work').condition(('time', 'morning'))

q.run()
print(q.format_answers(fmt='array'))
