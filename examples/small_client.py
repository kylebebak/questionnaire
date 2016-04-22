from questionnaire import Questionnaire
q = Questionnaire()

q.add_question('day', ['monday', 'friday', 'saturday'])
q.add_question('time', ['morning', 'evening', 'night'])

# saturday morning
q.add_question('todo', ['eat barbacoa', 'eat pozole'],
    multiple=True, keys=['day', 'time'], vals=['saturday', 'morning'])
# other mornings
q.add_question('todo', ['get dressed', 'walk the dog', 'go to work'],
    multiple=True, keys=['time'], vals=['morning'])
# friday or saturday, evening or night
q.add_question('todo', ['eat tostadas', 'go to the cantina'],
    multiple=True, keys=['day', 'time'], vals=[('friday', 'saturday'), ('evening', 'night')], operators=[lambda x, y: x in y]*2)
# monday night is skipped

choices = q.run()
print(choices)
