from questionnaire import Questionnaire

q = Questionnaire()
q.raw('age', prompt='How old are you?', type=int)

q.one('plans', 'Valley College', 'La Escuela de Calor', prompt='Where do you want to go to school?').condition(
    ('age', 18, '<='))
q.one('plans', 'On a farm', 'In an office', 'On the couch', prompt='Where do you want to work?', idx=2).condition(
    ('age', 40, '<='))
q.one('plans', 'El Caribe', 'Disneyland', 'Las Islas Canarias', prompt='Where do you want to vacation?').condition(
    ('age', 60, '<='))
q.one('plans', 'El campo', 'The beach', 'San Miguel de Allende', prompt='Where do you want to retire?')

q.run()
print(q.answers)
