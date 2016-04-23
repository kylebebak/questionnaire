from questionnaire import Questionnaire
q = Questionnaire()

q.add_question('day', options=['monday', 'friday', 'saturday'])
q.add_question('time', options=['morning', 'evening', 'night'])

# saturday morning
q.add_question('todo', prompter="multiple", options=['eat barbacoa', 'eat pozole']).\
    add_condition(keys=['day', 'time'], vals=['saturday', 'morning'])
# other mornings
q.add_question('todo', prompter="multiple", options=['get dressed', 'walk the dog', 'go to work']).\
    add_condition(keys=['time'], vals=['morning'])
# friday or saturday, evening or night
q.add_question('todo', prompter="multiple", options=['eat tostadas', 'go to the cantina']).\
    add_condition(keys=['day', 'time'], vals=[('friday', 'saturday'), ('evening', 'night')], operators=[lambda x, y: x in y]*2)
# monday night is skipped

q.add_question('age', prompter="raw", prompt='how old are you?', type=int)

answers = q.run()
print(answers)
