from questionnaire import Questionnaire


def not_blank(value):
    return 'enter a color' if not value else None


q = Questionnaire(show_answers=False, can_go_back=False)
q.raw('color', prompt='Favorite color (type ENTER to insert the default value):', default='blue').validate(not_blank)

q.run()
print(q.answers.get('color'))
