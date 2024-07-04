import yaml
import argparse
import datetime
import sys
from itertools import product
from copy import copy, deepcopy

##################### MACROURI #####################
INTERVALE = 'Intervale'
ZILE = 'Zile'
MATERII = 'Materii'
PROFESORI = 'Profesori'
SALI = 'Sali'

def read_yaml_file(file_path : str) -> dict:
    '''
    Citeste un fișier yaml și returnează conținutul său sub formă de dicționar
    '''
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def acces_yaml_attributes(yaml_dict : dict):
    '''
    Primește un dicționar yaml și afișează datele referitoare la atributele sale
    '''

    print('Zilele din orar sunt:', yaml_dict[ZILE])
    print()
    print('Intervalele orarului sunt:', yaml_dict[INTERVALE])
    print()
    print('Materiile sunt:', yaml_dict[MATERII])
    print()
    print('Profesorii sunt:', end=' ')
    print(*list(yaml_dict[PROFESORI].keys()), sep=', ')
    print()
    print('Sălile sunt:', end=' ')
    print(*list(yaml_dict[SALI].keys()), sep=', ')


def get_profs_initials(profs : list) -> dict:
    '''
    Primește o listă de profesori

    Returnează două dicționare:
    - unul care are numele profesorilor drept chei și drept valori prescurtările lor (prof_to_initials[prof] = initiale)
    - unul care are prescurtările profesorilor drept chei și drept valori numele lor (initials_to_prof[initiale] = prof)
    '''

    initials_to_prof = {}
    prof_to_initials = {}
    initials_count = {}

    for prof in profs:
        name_components = prof.split(' ')
        initials = name_components[0][0] + name_components[1][0]
        
        if initials in initials_count:
            initials_count[initials] += 1
            initials += str(initials_count[initials])
        else:
            initials_count[initials] = 1
        
        initials_to_prof[initials] = prof
        prof_to_initials[prof] = initials
        
    return prof_to_initials, initials_to_prof


def allign_string_with_spaces(s : str, max_len : int, allignment_type : str = 'center') -> str:
    '''
    Primește un string și un număr întreg

    Returnează string-ul dat, completat cu spații până la lungimea dată
    '''

    len_str = len(s)

    if len_str >= max_len:
        raise ValueError('Lungimea string-ului este mai mare decât lungimea maximă dată')
    

    if allignment_type == 'left':
        s = 6 * ' ' + s
        s += (max_len - len(s)) * ' '

    elif allignment_type == 'center':
        if len_str % 2 == 1:
            s = ' ' + s
        s = s.center(max_len, ' ')

    return s


def pretty_print_timetable_aux_zile(timetable : {str : {(int, int) : {str : (str, str)}}}, input_path : str) -> str:
    '''
    Primește un dicționar ce are chei zilele, cu valori dicționare de intervale reprezentate ca tupluri de int-uri, cu valori dicționare de săli, cu valori tupluri (profesor, materie)

    Returnează un string formatat să arate asemenea unui tabel excel cu zilele pe linii, intervalele pe coloane și în intersecția acestora, ferestrele de 2 ore cu materiile alocate în fiecare sală fiecărui profesor
    '''

    max_len = 30

    profs = read_yaml_file(input_path)[PROFESORI].keys()
    profs_to_initials, _ = get_profs_initials(profs)

    table_str = '|           Interval           |             Luni             |             Marti            |           Miercuri           |              Joi             |            Vineri            |\n'

    no_classes = len(timetable['Luni'][(8, 10)])

    first_line_len = 187
    delim = '-' * first_line_len + '\n'
    table_str = table_str + delim
    
    for interval in timetable['Luni']:
        s_interval = '|'
        
        crt_str = allign_string_with_spaces(f'{interval[0]} - {interval[1]}', max_len, 'center')

        s_interval += crt_str

        for class_idx in range(no_classes):
            if class_idx != 0:
                s_interval += f'|{30 * " "}'

            for day in timetable:
                classes = timetable[day][interval]
                classroom = list(classes.keys())[class_idx]

                s_interval += '|'

                if not classes[classroom]:
                    s_interval += allign_string_with_spaces(f'{classroom} - goala', max_len, 'left')
                else:
                    prof, subject = classes[classroom]
                    s_interval += allign_string_with_spaces(f'{subject} : ({classroom} - {profs_to_initials[prof]})', max_len, 'left')
            
            s_interval += '|\n'
        table_str += s_interval + delim

    return table_str

def pretty_print_timetable_aux_intervale(timetable : {(int, int) : {str : {str : (str, str)}}}, input_path : str) -> str:
    '''
    Primește un dicționar de intervale reprezentate ca tupluri de int-uri, cu valori dicționare de zile, cu valori dicționare de săli, cu valori tupluri (profesor, materie)

    Returnează un string formatat să arate asemenea unui tabel excel cu zilele pe linii, intervalele pe coloane și în intersecția acestora, ferestrele de 2 ore cu materiile alocate în fiecare sală fiecărui profesor
    '''

    max_len = 30

    profs = read_yaml_file(input_path)[PROFESORI].keys()
    profs_to_initials, _ = get_profs_initials(profs)

    table_str = '|           Interval           |             Luni             |             Marti            |           Miercuri           |              Joi             |            Vineri            |\n'

    no_classes = len(timetable[(8, 10)]['Luni'])

    first_line_len = 187
    delim = '-' * first_line_len + '\n'
    table_str = table_str + delim
    
    for interval in timetable:
        s_interval = '|' + allign_string_with_spaces(f'{interval[0]} - {interval[1]}', max_len, 'center')

        for class_idx in range(no_classes):
            if class_idx != 0:
                s_interval += '|'

            for day in timetable[interval]:
                classes = timetable[interval][day]
                classroom = list(classes.keys())[class_idx]

                s_interval += '|'

                if not classes[classroom]:
                    s_interval += allign_string_with_spaces(f'{classroom} - goala', max_len, 'left')
                else:
                    prof, subject = classes[classroom]
                    s_interval += allign_string_with_spaces(f'{subject} : ({classroom} - {profs_to_initials[prof]})', max_len, 'left')
            
            s_interval += '|\n'
        table_str += s_interval + delim

    return table_str

def pretty_print_timetable(timetable : dict, input_path : str) -> str:
    '''
    Poate primi fie un dictionar de zile conținând dicționare de intervale conținând dicționare de săli cu tupluri (profesor, materie)
    fie un dictionar de intervale conținând dictionare de zile conținând dicționare de săli cu tupluri (profesor, materie)
    
    Pentru cazul în care o sală nu este ocupată la un moment de timp, se așteaptă 'None' în valoare, în loc de tuplu
    '''
    if 'Luni' in timetable:
        return pretty_print_timetable_aux_zile(timetable, input_path)
    else:
        return pretty_print_timetable_aux_intervale(timetable, input_path)


teacher_hours_register = {}
rooms_register = {}
course_a_week = {}

def courses_per_week(val, max_times_per_course, domains):
    global course_a_week
    number_times = max_times_per_course[val[1]]

    result = course_a_week.get(val[1], 0)
    
    if result < number_times:
        result += 1
        course_a_week[val[1]] = result
        if result == number_times:
            for key, list_vals in domains.items():
                for val in list_vals:
                    if val[1] in val:
                        list_vals.remove(val)
                domains[key] = list_vals

        return True
    elif result >= number_times:
        return False



def teachers_intervals(val, domains):
    global teacher_hours_register
    if len(val) != 0:
        number_intervals = teacher_hours_register.get(val[0], 0)
        if number_intervals < 7:
            number_intervals += 1
            teacher_hours_register[val[0]] = number_intervals
            if number_intervals == 7:
                for key, list_values in domains.items():
                    for value in list_values:
                        if val[0] in value:
                            list_values.remove(value)
                    domains[key] = list_values
            return True
        elif number_intervals > 7:
            return False

def teachers_individual(var, val, solution):
    for key, value in solution.items():
        if len(value) != 0:
            if key[0] == var[0] and key[1] == var[1] and val[0] == value[0]:
                    return False
    
    return True
        

def soft_constraints(val, constraints_val):
    for constraint in constraints_val:
        if constraint.startswith("!"):
            if constraint[1:] == val[0] or constraint[1:] == val[1]:
                return False
    return True

def PCSP(vars, domains, constraints, acceptable_cost, solution, cost):
    global best_solution
    global best_cost
    global iterations
    best_solution = {}
    best_cost = len(constraints)
    iterations = 0
    
    if not vars:
        if cost < best_cost:
          best_solution = deepcopy(solution)
          best_cost = cost
        if cost <= acceptable_cost:
            return True
        return False
    elif not domains[vars[0]]:
        new_solution = solution.copy()
        new_solution[vars[0]] = ()
        new_cost = cost
        return PCSP(vars[1:], deepcopy(domains), constraints, acceptable_cost, new_solution, new_cost)
    elif cost == best_cost:
        return False
    else: 
        var = vars[0]
        val = domains[var].pop(0)
        iterations += 1

        new_solution = solution.copy()
        new_solution[var] = val

        new_cost = cost
        check_course = True
        if teachers_individual(var, val, solution) == False:
            new_cost += 1
            check_course = False

        if teachers_intervals(val, domains) == False:
            new_cost += 1
            
        if check_course == True:
            if courses_per_week(val, max_courses_per_week ,domains) == False:
                new_cost += 1
            
        if soft_constraints(val, Profesori[val[0]]['Constrangeri']) == False:
            new_cost += 1

        if (new_cost < best_cost) and (new_cost <= acceptable_cost):
            if PCSP(vars[1:], deepcopy(domains), constraints, acceptable_cost, new_solution, new_cost):
                return True
        return PCSP(vars, domains, constraints, acceptable_cost, solution, cost)


def convert_format(input_data):
    table = {}
    for key, value in input_data.items():
        day = key[0]
        interval = key[1]
        room = key[2]
        table[day] = table.get(day, {})
        table[day][interval] = table[day].get(interval, {})
        table[day][interval][room] = value
    
    return table



if __name__ == '__main__':
    filename = f'inputs/dummy.yaml'

    global max_courses_per_week
    max_courses_per_week = {}
    text = input("The algorithm is: ")

    timetable_specs = read_yaml_file(filename)
    Intervale_orare = timetable_specs['Intervale']
    Materii = timetable_specs['Materii']
    Zile = timetable_specs['Zile']
    Profesori = timetable_specs['Profesori'] 
    Sali = timetable_specs['Sali']

    for name_room, room_details in Sali.items():
        capacity = room_details['Capacitate']
        courses = room_details['Materii']
        for course in courses:
            number = Materii[course]
            max_courses_per_week[course] = int(number / capacity)


    profesori_constragerile_lor = []
    for nume, detalii_profesor in Profesori.items():
        profesori_constragerile_lor.append((nume, detalii_profesor))
    
    Domains = {}
    Vars = []
    Vals = []
    
    all_constraints = []
    Ints_intervale_orare = []
    for interval_orar in Intervale_orare:
        Ints_intervale_orare.append(eval(interval_orar))
    
    combinations_all = list(product(Zile, Ints_intervale_orare, Sali))
    Vars = combinations_all

    for combination in combinations_all:
        list_teachers = []
        for name, constraints in profesori_constragerile_lor:
            days = []
            hours = []
            Courses_in_room = Sali[combination[2]]['Materii']
            courses = constraints['Materii']
            day = combination[0]
            time = combination[1]
            for course_Teacher in courses:
                if course_Teacher in Courses_in_room:
                    for constraint in constraints['Constrangeri']:
                        if not constraint.startswith("!"):
                            if any(char.isdigit() for char in constraint):
                                substrings = constraint.split('-')
                                numbers = []
                                for substr in substrings:
                                    numbers.append(int(substr))
                                if (numbers[1] - numbers[0]) > 2 and (numbers[1] - numbers[0]) % 2 == 0:
                                    for number in numbers:
                                        if number + 2 < numbers[len(numbers) - 1]:
                                            numbers.append(number + 2)
                                    numbers = sorted(numbers)
                                    pairs = []
                                    for i in range(len(numbers) - 1):
                                        pairs.append((numbers[i], numbers[i + 1]))
                                    constraint = pairs
                                    for pair in constraint:
                                        hours.append(pair)
                                elif numbers[1] - numbers[0] == 2:
                                    numbers = sorted(numbers)
                                    for i in range(len(numbers) - 1):
                                        hours.append((numbers[i], numbers[i + 1]))   
                            else:
                                days.append(constraint)
                    if day in days:
                        if isinstance(time, str):
                            substrs = time.replace("(", "").replace(")", "")
                            substrs = substrs.split(",")
                        else:
                            time = str(time)
                            substrs = time.replace("(", "").replace(")", "")
                            substrs = substrs.split(",")

                        numbers = []
                        for substr in substrs:
                            numbers.append(int(substr))
                        time = (numbers[0], numbers[1])
                        for tuple_time in hours:
                            if time[0] == tuple_time[0] and time[1] == tuple_time[1]:
                                result = Domains.get(combination, 0)
                                if result == 0:
                                    list_teachers.append((name, course_Teacher))
                                    Domains[combination] = sorted(list(set(list_teachers)))
                                else:
                                    list_teachers.append((name, course_Teacher))
                                    Domains[combination] = sorted(list(set(list_teachers)))
                    
    for combination in combinations_all:
        for name, constraints in profesori_constragerile_lor:
            Courses_in_room = Sali[combination[2]]['Materii']
            courses = constraints['Materii']
            day = combination[0]
            time = combination[1]
            for course_Teacher in courses:
                 if course_Teacher in Courses_in_room:
                    result = Domains.get(combination, [])
                    if (name, course_Teacher) not in  Domains:
                        if result == []:
                            result.append((name, course_Teacher))
                            Domains[combination] = sorted(list(set(result)), key=lambda x: x[1])
                        else:
                            result.append((name, course_Teacher))
                            unique_list = list(set(result))
                            sorted_unique = sorted(unique_list, key=lambda x: x[1])
                            Domains[combination] = sorted_unique
    
    for var in Vars:
        for val in Domains[var]:
            all_constraints.append(([var, val], teachers_individual))
    
    for key, val in Domains.items():
        for elem in val:
            Constraints_teacher = Profesori[elem[0]]['Constrangeri']
            all_constraints.append(([val, Constraints_teacher], soft_constraints))

    for key, val in Domains.items():
        for tuple_t in val:
            all_constraints.append((tuple_t, teachers_intervals))
        
    for key, val in Domains.items():
        for tuple_t in val:
            all_constraints.append(([tuple_t, max_courses_per_week, Domains], courses_per_week))


    if text == 'pcsp':
        best_solution = {}
        best_cost = len(all_constraints)
        iterations = 0

        table = PCSP(Vars, deepcopy(Domains), all_constraints, 0, {}, 0)

        if table:
            print(f"Best found in {iterations} iterations: {str(best_cost)} - {str(best_solution)}")
        else:
            print(f"Acceptable solution not found in {iterations}; Best found: {str(best_cost)} - {str(best_solution)}")

        convert = convert_format(best_solution)

        print(pretty_print_timetable(convert, 'inputs/dummy.yaml'))

