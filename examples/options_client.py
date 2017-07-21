from questionnaire import Questionnaire
q = Questionnaire(out_type='plain')

q.add_question('options', prompt='Choose some options', prompter='multiple',
               options=['Option 1', 'Option 2', 'Option 3', 'Option 4'], all=None)

answers = q.run()
