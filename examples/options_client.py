from questionnaire import Questionnaire
q = Questionnaire(can_go_back=False)

q.add_question('options', prompt='Choose some options', prompter='multiple',
               options=['Option 1', 'Option 2', 'Option 3', 'Option 4'], all=None)
q.add_question('more', prompt='Choose some more', prompter='multiple',
               options=['Option 5', 'Option 6'], all=None)

q.run()
print(q.answers)

q.add_question('yet_more', prompt='And more...', prompter='multiple',
               options=['Option 7', 'Option 8'], all=None)
q.add_question('done', prompt='Last ones', prompter='multiple',
               options=['Option 9', 'Option 10'], all=None)
q.add_question('password', prompt='Password?', prompter='raw', secret=True)

q.ask_question()
q.ask_question()
q.ask_question()
print(q.answers)
