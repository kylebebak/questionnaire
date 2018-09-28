from questionnaire import Questionnaire
import requests

q = Questionnaire(show_answers=False, can_go_back=False)
q.raw('color', prompt='Favorite color (type ENTER to insert the default value):', default='blue')

q.run()
print(q.answers.get('color'))
