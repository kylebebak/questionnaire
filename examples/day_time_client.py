from questionnaire import Questionnaire
q = Questionnaire()

q.add_question('day', prompt='What day is it?', options=['monday', 'friday', 'saturday'])
q.add_question('time', prompt='What time is it?', options=['morning', 'night'],
               verbose_options=['in the morning', 'at night'])

answers = q.run()
