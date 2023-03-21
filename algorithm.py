import algorithm_matrix

'''Здесь номера индексов отвечают за следующие аспекты:
0 - дружба, 1 - страсть, 2 - любовь, 3 - конфликт, 4 - страдание, 5 - ключевой аспект'''
list_coefficients = [3, 2, 5, -2, -4, 5]
error_rate_for_angle = 4

from_zs_to_idx = {'Овен': 0, 'Телец': 1, 'Близнецы': 2, 'Рак': 3, 'Лев': 4, 'Дева': 5, 'Весы': 6, 'Скорпион': 7,
                  'Стрелец': 8, 'Козерог': 9, 'Водолей': 10, 'Рыбы': 11}
num_planets = 10
num_minutes = 60
num_degrees_for_one_zs = 30
all_degrees = 360
angle_zero = 0
angle_sixteen = 60
angle_square = 90
angle_without_sixteen = 120
angle_opposition = 180


def get_list_planets_degrees(list_input):
    list_zs = []
    list_degrees = []
    list_minutes = []
    for i in range(0, num_planets):
        list_zs.append(list_input[3 * i])
        list_degrees.append(list_input[3 * i + 1])
        list_minutes.append(list_input[3 * i + 2])
    list_planets_degrees = []
    for i in range(0, num_planets):
        list_planets_degrees.append(from_zs_to_idx[list_zs[i]] * num_degrees_for_one_zs + list_degrees[i]
                                    + list_minutes[i] / num_minutes)
    return list_planets_degrees


def calculate_list_combination(list_planets_degrees1, list_planets_degrees2):
    list_combination = [0, 0, 0, 0, 0, 0]
    for planet1 in range(0, num_planets):
        for planet2 in range(0, num_planets):
            angle = min(abs(list_planets_degrees1[planet1] - list_planets_degrees2[planet2]),
                        all_degrees - abs(list_planets_degrees1[planet1] - list_planets_degrees2[planet2]))
            if abs(angle - angle_zero) <= error_rate_for_angle:
                type_angle = 0
            elif abs(angle - angle_sixteen) <= error_rate_for_angle:
                type_angle = 1
            elif abs(angle - angle_square) <= error_rate_for_angle:
                type_angle = 2
            elif abs(angle - angle_without_sixteen) <= error_rate_for_angle:
                type_angle = 3
            elif abs(angle - angle_opposition) <= error_rate_for_angle:
                type_angle = 4
            else:
                type_angle = -1
            if type_angle != -1:
                for elem in algorithm_matrix.matrix_planets_angle_aspects[planet1][planet2][type_angle]:
                    list_combination[elem] += 1
    return list_combination


def get_points_from_list_combinations_linear_algorithm(list_combination, coefficients):
    points = 0
    for i in range(0, len(list_combination)):
        points += list_combination[i] * coefficients[i]
    return points


def get_sorted_candidates(main_person, candidates):
    list_point_idx = []
    for i in range(0, len(candidates)):
        list_combination = calculate_list_combination(main_person, candidates[i])
        points = get_points_from_list_combinations_linear_algorithm(list_combination, list_coefficients)
        list_point_idx.append([points, candidates[i][-1]])
    list_point_idx.sort(reverse=True)
    final_sort_idx = []
    for elem in list_point_idx:
        final_sort_idx.append(elem[1])
    return final_sort_idx
