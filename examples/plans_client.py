from questionnaire import Questionnaire

q = Questionnaire()
q.add_question('age', prompter="raw", prompt='How old are you?', type=int)

# youngsters (age less than or equal to 18)
q.add_question('plans', prompt="Where do you want to go to school?", options=['Valley College', 'La Escuela de Calor']).\
    add_condition(keys=['age'], vals=[18], operators=['<=='])
q.add_question('plans', prompt="Where do you want to work?", options=['On a farm', 'In an office', 'On the couch']).\
    add_condition(keys=['age'], vals=[40], operators=['<='])
q.add_question('plans', prompt="Where do you want to vacation?", options=['El Caribe', 'On a cruise ship', 'Las Islas Canarias']).\
    add_condition(keys=['age'], vals=[60], operators=['<='])
# old folks (more than 60 years old)
q.add_question('plans', prompt="Where do you want to retire?", options=['El campo', 'The beach', 'San Miguel de Allende'])

answers = q.run()
