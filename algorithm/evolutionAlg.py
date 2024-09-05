import numpy as np
import random
import copy
import os

k = 1
population_size = 100 * k
generation = 0  # global variable - represents the generation number
total_fitness_calls = 0
steps = 0

# weight
cost_weight = 10
contracts_weight = 1000
requirements_weight = 10
idle_workers_weight = 100

# map of the relevant_shifts
relevant_shifts = {}

# 14: {
#         "id": 14,
#         "profession": "Doctor",
#         "day": "Monday",
#         "startHour": "10:00",
#         "endHour": "13:00",
#         "cost": 50
#     },


shifts_to_requirements_map = {}
# 2 : {[{"id": 1, "profession": "Teacher", "day": "Wednesday", "hour": "14:00", "number": 8},
#       {"id": 3, "profession": "Teacher", "day": "Wednesday", "hour": "16:00", "number": 7}]}

possible_shifts_to_workers_map = {}
# 2 : {[33146, 33147, 33148]}

shifts_list = []
#     [
#     # Doctor Shifts
#     {"id": 1, "profession": "Doctor", "day": "Sunday", "startHour": "08:00", "endHour": "13:00", "cost": 50},
#     {"id": 2, "profession": "Doctor", "day": "Sunday", "startHour": "13:00", "endHour": "16:00", "cost": 50},
#     {"id": 3, "profession": "Doctor", "day": "Sunday", "startHour": "16:00", "endHour": "19:00", "cost": 50},
#     {"id": 4, "profession": "Doctor", "day": "Sunday", "startHour": "19:00", "endHour": "21:00", "cost": 50},
#     {"id": 5, "profession": "Doctor", "day": "Sunday", "startHour": "09:00", "endHour": "16:00", "cost": 50},
#     {"id": 6, "profession": "Doctor", "day": "Sunday", "startHour": "12:00", "endHour": "17:00", "cost": 50},
#     {"id": 7, "profession": "Doctor", "day": "Sunday", "startHour": "15:00", "endHour": "20:00", "cost": 50},
#
#     # Teacher Shifts
#     {"id": 8, "profession": "Teacher", "day": "Sunday", "startHour": "08:00", "endHour": "10:00", "cost": 50},
#     {"id": 9, "profession": "Teacher", "day": "Sunday", "startHour": "11:00", "endHour": "14:00", "cost": 50},
#     {"id": 10, "profession": "Teacher", "day": "Sunday", "startHour": "14:00", "endHour": "16:00", "cost": 50},
#     {"id": 11, "profession": "Teacher", "day": "Sunday", "startHour": "18:00", "endHour": "22:00", "cost": 50},
# ]

workers_map = {}
#     {
#     1: {"id": 1, "name": "Worker 1", "professions": ["Doctor", "Teacher"], "days": ["Sunday"], "relevant_shifts_id": [],
#         "hours_per_week": 9},
#     2: {"id": 2, "name": "Worker 2", "professions": ["Doctor", "Teacher"], "days": ["Sunday"], "relevant_shifts_id": [],
#         "hours_per_week": 11},
#     3: {"id": 3, "name": "Worker 3", "professions": ["Doctor", "Teacher"], "days": ["Sunday"], "relevant_shifts_id": [],
#         "hours_per_week": 10},
#     4: {"id": 4, "name": "Worker 4", "professions": ["Doctor", "Teacher"], "days": ["Sunday"], "relevant_shifts_id": [],
#         "hours_per_week": 8},
#     5: {"id": 5, "name": "Worker 5", "professions": ["Doctor", "Teacher"], "days": ["Sunday"], "relevant_shifts_id": [],
#         "hours_per_week": 10},
#     6: {"id": 6, "name": "Worker 6", "professions": ["Doctor", "Teacher"], "days": ["Sunday"], "relevant_shifts_id": [],
#         "hours_per_week": 10},
#     7: {"id": 7, "name": "Worker 7", "professions": ["Doctor", "Teacher"], "days": ["Sunday"], "relevant_shifts_id": [],
#         "hours_per_week": 7},
#     8: {"id": 8, "name": "Worker 8", "professions": ["Doctor", "Teacher"], "days": ["Sunday"], "relevant_shifts_id": [],
#         "hours_per_week": 5},
#     9: {"id": 9, "name": "Worker 9", "professions": ["Doctor", "Teacher"], "days": ["Sunday"], "relevant_shifts_id": [],
#         "hours_per_week": 11},
#     10: {"id": 10, "name": "Worker 10", "professions": ["Doctor", "Teacher"], "days": ["Sunday"],
#          "relevant_shifts_id": [], "hours_per_week": 8},
#     11: {"id": 11, "name": "Worker 11", "professions": ["Doctor", "Teacher"], "days": ["Sunday"],
#          "relevant_shifts_id": [], "hours_per_week": 6}
# }

requirements_list = []
#     [
#     {"id": 1, "profession": "Doctor", "day": "Sunday", "hour": "08:00", "number": 2},
#     {"id": 2, "profession": "Doctor", "day": "Sunday", "hour": "09:00", "number": 2},
#     {"id": 3, "profession": "Doctor", "day": "Sunday", "hour": "10:00", "number": 4},
#     {"id": 4, "profession": "Doctor", "day": "Sunday", "hour": "11:00", "number": 5},
#     {"id": 5, "profession": "Doctor", "day": "Sunday", "hour": "13:00", "number": 6},
#     {"id": 6, "profession": "Doctor", "day": "Sunday", "hour": "16:00", "number": 8},
#     {"id": 7, "profession": "Doctor", "day": "Sunday", "hour": "17:00", "number": 4},
#     {"id": 8, "profession": "Doctor", "day": "Sunday", "hour": "19:00", "number": 3},
#     {"id": 9, "profession": "Doctor", "day": "Sunday", "hour": "20:00", "number": 2},
#
#     {"id": 10, "profession": "Teacher", "day": "Sunday", "hour": "08:00", "number": 3},
#     {"id": 11, "profession": "Teacher", "day": "Sunday", "hour": "09:00", "number": 2},
#     {"id": 12, "profession": "Teacher", "day": "Sunday", "hour": "11:00", "number": 1},
#     {"id": 13, "profession": "Teacher", "day": "Sunday", "hour": "13:00", "number": 3},
#     {"id": 14, "profession": "Teacher", "day": "Sunday", "hour": "14:00", "number": 2},
#     {"id": 15, "profession": "Teacher", "day": "Sunday", "hour": "15:00", "number": 2},
#     {"id": 16, "profession": "Teacher", "day": "Sunday", "hour": "18:00", "number": 3},
#     {"id": 17, "profession": "Teacher", "day": "Sunday", "hour": "21:00", "number": 4},
# ]

requirements_num_map = {}
# 1 : {8}

worker_construct_map = {}
# 33146 : {15}

worker_possible_shifts_map = {}


# 33146 : {[1, 2, 3]}


def is_hour_in_range(hour, start_hour, end_hour):
    # Convert hour, start_hour, and end_hour to integers for comparison
    hour_int = int(hour.replace(':', ''))
    start_hour_int = int(start_hour.replace(':', ''))
    end_hour_int = int(end_hour.replace(':', ''))

    # Check if the hour falls within the range
    return start_hour_int <= hour_int < end_hour_int


def convert_to_minutes(time):
    hours, minutes = map(int, time.split(":"))
    return hours * 60 + minutes


def duration_of_shift(my_shift_id):
    start = convert_to_minutes(relevant_shifts[my_shift_id]["startHour"])
    end = convert_to_minutes(relevant_shifts[my_shift_id]["endHour"])

    return (end - start) / 60


def is_overlap(shift1_id, shift2_id):
    start1 = convert_to_minutes(relevant_shifts[shift1_id]["startHour"])
    end1 = convert_to_minutes(relevant_shifts[shift1_id]["endHour"])
    start2 = convert_to_minutes(relevant_shifts[shift2_id]["startHour"])
    end2 = convert_to_minutes(relevant_shifts[shift2_id]["endHour"])

    return (
            ((start2 <= start1 <= end2) or
             (start2 <= end1 <= end2) or
             (start1 <= start2 <= end1) or
             (start1 <= end2 <= end1)) and
            relevant_shifts[shift1_id]["day"] == relevant_shifts[shift2_id]["day"]
    )


def get_the_not_overlap_shifts(my_shift_id, shift_id_list):
    shift_id_list_copy = copy.deepcopy(shift_id_list)  # Use deepcopy to avoid altering the original list

    for shift_id in shift_id_list_copy[:]:  # Iterate over a copy to avoid skipping elements
        if is_overlap(shift_id, my_shift_id):
            shift_id_list_copy.remove(shift_id)

    return shift_id_list_copy


def get_the_overlap_shifts(my_shift_id, shift_id_list):
    shift_id_list_copy = copy.deepcopy(shift_id_list)  # Use deepcopy to avoid altering the original list

    for shift_id in shift_id_list_copy[:]:  # Iterate over a copy to avoid skipping elements
        if not is_overlap(shift_id, my_shift_id):
            shift_id_list_copy.remove(shift_id)

    return shift_id_list_copy


def get_lap_shifts_id(my_shift_id):
    lap_shifts_id_array = []

    for shift_id in relevant_shifts.keys():
        if is_overlap(my_shift_id, shift_id):
            lap_shifts_id_array.append(shift_id)

    return lap_shifts_id_array


def get_relevant_requirements_for_shift(shift):
    requirements_array = []
    for requirement in requirements_list:
        if requirement['day'] == shift['day'] \
                and requirement['profession'] == shift['profession'] \
                and is_hour_in_range(requirement['hour'], shift['startHour'], shift['endHour']):
            requirements_array.append(requirement)

    return requirements_array


def get_relevant_shifts_for_requirement(requirement):
    shift_id_array = []
    for shift_id, shift_info in relevant_shifts.items():
        if requirement['day'] == shift_info['day'] \
                and requirement['profession'] == shift_info['profession'] \
                and is_hour_in_range(requirement['hour'], shift_info['startHour'], shift_info['endHour']):
            shift_id_array.append(shift_id)

    return shift_id_array


def initialize():
    # initialize the relevant_shifts_id
    for shift in shifts_list:
        for req in requirements_list:
            if req['profession'] == shift['profession'] and req['day'] == shift['day'] and is_hour_in_range(req['hour'],
                                                                                                            shift[
                                                                                                                'startHour'],
                                                                                                            shift[
                                                                                                                'endHour']):
                relevant_shifts[shift['id']] = shift
                break

    # initialize the relevant_shifts_id for every worker
    for worker_id, worker_info in workers_map.items():
        for shift in relevant_shifts.values():
            if shift['day'] in worker_info['days'] and shift['profession'] in worker_info['professions']:
                worker_info['relevant_shifts_id'].append(shift['id'])

    # initialize the shifts_to_workers_map
    for worker_id, worker_info in workers_map.items():
        for shift_id in worker_info["relevant_shifts_id"]:
            if shift_id not in possible_shifts_to_workers_map:
                possible_shifts_to_workers_map[shift_id] = []
            if worker_id not in possible_shifts_to_workers_map[shift_id]:
                possible_shifts_to_workers_map[shift_id].append(worker_id)

    # initialize the worker_construct_map
    for worker_id, worker_info in workers_map.items():
        worker_construct_map[worker_id] = worker_info['hours_per_week']

    # initialize the worker_possible_shifts_map
    for worker_id, worker_info in workers_map.items():
        worker_possible_shifts_map[worker_id] = worker_info['relevant_shifts_id']

    # initialize the shifts_to_requirements_map
    for shift_id, shift_info in relevant_shifts.items():
        shifts_to_requirements_map[shift_id] = get_relevant_requirements_for_shift(shift_info)

    # initialize the requirements_num_map
    for requirement in requirements_list:
        requirement_id = requirement['id']
        num = requirement['number']
        requirements_num_map[requirement_id] = num


def generate_new_solutions(num):
    solutions_array = []
    by_require_num = 10

    # by worker construct
    for i in range(num - by_require_num):
        solution = []

        for worker_id, worker_info in workers_map.items():

            contract_hours_left = worker_info['hours_per_week']
            worker_relevant_shift_id = worker_info['relevant_shifts_id'].copy()

            while contract_hours_left > 0 and len(worker_relevant_shift_id):
                shift_id_sample = random.choices(list(worker_info['relevant_shifts_id']), k=1)
                shift_id_sample = shift_id_sample[0]

                contract_hours_left -= duration_of_shift(shift_id_sample)
                worker_relevant_shift_id = get_the_not_overlap_shifts(shift_id_sample, worker_relevant_shift_id)

                solution.append((worker_id, shift_id_sample))

        solutions_array.append(solution)

    # by require
    for i in range(by_require_num):

        solution = []
        shifts_to_workers = copy.deepcopy(possible_shifts_to_workers_map)

        for requirement in requirements_list:
            requirement_shifts = get_relevant_shifts_for_requirement(requirement)
            if len(requirement_shifts) == 0:
                continue
            requirement_workers_left = requirement['number']

            counter = 0

            while requirement_workers_left and counter < 3:
                shift_id_sample = random.choices(list(requirement_shifts), k=1)
                shift_id_sample = shift_id_sample[0]
                if shift_id_sample not in shifts_to_workers.keys() or len(shifts_to_workers[shift_id_sample]) == 0:
                    counter += 1
                    continue

                worker_id_sample = random.choices(list(shifts_to_workers[shift_id_sample]), k=1)
                worker_id_sample = worker_id_sample[0]

                requirement_workers_left -= 1
                counter = 0

                worker_relevant_shift_id = workers_map[worker_id_sample]['relevant_shifts_id'].copy()
                overlap_shifts = get_the_overlap_shifts(shift_id_sample, worker_relevant_shift_id)

                for shift_id in overlap_shifts:
                    if worker_id_sample in shifts_to_workers[shift_id]:
                        shifts_to_workers[shift_id].remove(worker_id_sample)

                solution.append((worker_id_sample, shift_id_sample))

        solutions_array.append(solution)

    solutions_array = improve_solutions(solutions_array, 0.5)
    return solutions_array


def get_fitness_with_more_info(solution):
    # the same as get fitness - but return also the cost, satisfied_contracts, satisfied_requirements, idle_workers

    fitness = 2000

    cost = 0
    satisfied_contracts = 0
    satisfied_requirements = 0
    idle_workers = 0
    total_requirements_num = 0

    constructs = copy.deepcopy(worker_construct_map)
    left_requirements_num_map = copy.deepcopy(requirements_num_map)

    # loop over the solution
    for item in solution:
        worker_id = item[0]
        shift_id = item[1]

        # update cost
        cost += relevant_shifts[shift_id]['cost']

        # update constructs
        constructs[worker_id] -= duration_of_shift(shift_id)

        # update left_requirements and idle_workers
        idle_flag = True
        for requirement in get_relevant_requirements_for_shift(relevant_shifts[shift_id]):
            requirement_id = requirement['id']
            if left_requirements_num_map[requirement_id]:
                left_requirements_num_map[requirement_id] -= 1
                idle_flag = False
        if idle_flag:
            idle_workers += 1

    # calculate satisfied_contracts
    for left_construct in constructs.values():
        if left_construct <= 0:
            satisfied_contracts += 1

    # calculate total_requirements_num
    for requirement in requirements_list:
        total_requirements_num += requirement['number']

    # calculate satisfied_requirements
    satisfied_requirements += total_requirements_num
    for num in left_requirements_num_map.values():
        satisfied_requirements -= num

    # lower fitness is better fitness
    fitness += cost * cost_weight
    fitness += idle_workers * idle_workers_weight
    fitness -= satisfied_contracts * contracts_weight
    fitness -= satisfied_requirements * requirements_weight

    return fitness, cost, satisfied_contracts, satisfied_requirements, idle_workers, total_requirements_num


def get_fitness(solution):
    fitness = 2000

    cost = 0
    satisfied_contracts = 0
    satisfied_requirements = 0
    idle_workers = 0

    constructs = copy.deepcopy(worker_construct_map)
    left_requirements_num_map = copy.deepcopy(requirements_num_map)

    # loop over the solution
    for item in solution:
        worker_id = item[0]
        shift_id = item[1]

        # update cost
        cost += relevant_shifts[shift_id]['cost']

        # update constructs
        constructs[worker_id] -= duration_of_shift(shift_id)

        # update left_requirements and idle_workers
        idle_flag = True
        for requirement in get_relevant_requirements_for_shift(relevant_shifts[shift_id]):
            requirement_id = requirement['id']
            if left_requirements_num_map[requirement_id]:
                left_requirements_num_map[requirement_id] -= 1
                idle_flag = False
        if idle_flag:
            idle_workers += 1

    # calculate satisfied_contracts
    for left_construct in constructs.values():
        if left_construct <= 0:
            satisfied_contracts += 1

    # calculate satisfied_requirements
    for requirement in requirements_list:
        satisfied_requirements += requirement['number']

    for num in left_requirements_num_map.values():
        satisfied_requirements -= num

    # lower fitness is better fitness
    fitness += cost * cost_weight
    fitness += idle_workers * idle_workers_weight
    fitness -= satisfied_contracts * contracts_weight
    fitness -= satisfied_requirements * requirements_weight

    return fitness


def get_fitness_array(solutions):
    """
    :param solutions: the array which represents the whole population of different solutions
    :return:
    """
    # array of solutions and their fitness
    fitness_array = []
    for i in range(len(solutions)):
        solution = solutions[i]
        fitness_i = get_fitness(solution)

        # tuple with the index of the solution and its fitness
        fitness_tuple = (i, fitness_i)
        fitness_array.append(fitness_tuple)
    # sort fitness array according to fitness
    sorted_fitness_array = sorted(fitness_array, key=lambda x: x[1])

    if generation % 10 == 0:  # display the lowest fitness permutation every 10 generations
        index_of_best_solution = sorted_fitness_array[0][0]
        fitness, cost, satisfied_contracts, satisfied_requirements, idle_workers, total_requirement_num = get_fitness_with_more_info(
            solutions[index_of_best_solution])
        print("lowest_fitness prem: " + str(solutions[index_of_best_solution]))
        print("json: " + str(json_print(solutions[index_of_best_solution])))
        print("fitness: " + str(fitness))
        print("cost: " + str(cost))
        print("satisfied_contracts: " + str(satisfied_contracts) + ' / ' + str(len(workers_map)))
        print("satisfied_requirements: " + str(satisfied_requirements) + ' / ' + str(total_requirement_num))
        print("idle_workers: " + str(idle_workers))
        print()

    return sorted_fitness_array


def json_print(data):
    result = {}
    for item in data:
        if item[1] not in result:
            result[item[1]] = []
        result[item[1]].append(item[0])

    return result


def crossover(solutions):
    """
    selects random pair of solutions and does crossover between them
    :param solutions: list of 120 solutions
    :return: crossover results - list of 60 solutions
    """
    crossover_results = []
    num = len(solutions) - 1
    copied_solutions = solutions.copy()  # Create a copy of the solutions list

    for i in range(int(len(solutions) / 2)):
        per_one_idx = per_two_idx = 0
        # while the 2 random indexes are equal, choose 2 random indexes again
        while per_one_idx == per_two_idx:
            per_one_idx = random.randint(0, num)
            per_two_idx = random.randint(0, num)

        one = copied_solutions[per_one_idx]  # Use the copied_solutions list
        two = copied_solutions[per_two_idx]  # Use the copied_solutions list

        # pop indexes from permutations list so that the algorithm does not choose them again
        if per_one_idx > per_two_idx:
            copied_solutions.pop(per_one_idx)
            copied_solutions.pop(per_two_idx)
        else:
            copied_solutions.pop(per_two_idx)
            copied_solutions.pop(per_one_idx)

        common_length = min(len(one), len(two))

        num -= 2
        index = random.randint(0, max(0, common_length - 2))  # choose random index for crossover
        new_solution = []

        # the first part of new solution is from the first part of the first solution
        new_solution[0:index] = one[0:index]

        # the second part of new solution is from the second part of the second solution
        new_solution[index:] = two[index:]

        crossover_results.append(new_solution)

    # THE OUTPUT HERE IS NOT LEGAL!!!
    # it has to get through "improve_solutions" for correct_overlap (and optimization and mutations)
    return crossover_results


def improve_solutions(solutions, prob):
    improved_solutions = []

    # 5 best solutions get only correct_overlap and optimization, without mutations
    for solution in solutions[:5 * k]:
        approved_solution = []

        workers_possible_shifts_left = copy.deepcopy(worker_possible_shifts_map)

        for item in solution:
            worker_id = item[0]
            shift_id = item[1]

            if shift_id in workers_possible_shifts_left[worker_id]:
                # add the legal shift
                approved_solution.append(item)

                # remove the overlap shifts from the remain possible shifts
                overlap_shifts = get_the_overlap_shifts(shift_id, workers_possible_shifts_left[worker_id])

                for shift in overlap_shifts:
                    if shift in workers_possible_shifts_left[worker_id]:
                        workers_possible_shifts_left[worker_id].remove(shift)

        # remove optimization
        counter = 0
        fitness = get_fitness(approved_solution)

        while counter < 2 and len(approved_solution) > 1:
            opt_solution = copy.deepcopy(approved_solution)
            # random remove
            index_to_remove = random.randint(0, len(opt_solution) - 1)
            opt_solution.pop(index_to_remove)
            new_fitness = get_fitness(opt_solution)

            if new_fitness < fitness:
                approved_solution = opt_solution
                # counter = 0
            else:
                counter += 1

        # add optimization
        counter = 0
        fitness = get_fitness(approved_solution)

        while counter < 2:
            opt_solution = copy.deepcopy(approved_solution)
            worker_id = random.choices(list(workers_map.keys()), k=1)
            worker_id = worker_id[0]

            if len(workers_possible_shifts_left[worker_id]):
                shift_id = random.choices(list(workers_possible_shifts_left[worker_id]), k=1)
                shift_id = shift_id[0]
                opt_solution.append((worker_id, shift_id))
                new_fitness = get_fitness(opt_solution)

                if new_fitness < fitness:
                    # counter = 0
                    approved_solution = opt_solution
                    # remove the overlap shifts from the remain possible shifts
                    overlap_shifts = get_the_overlap_shifts(shift_id, workers_possible_shifts_left[worker_id])
                    for shift in overlap_shifts:
                        if shift in workers_possible_shifts_left[worker_id]:
                            workers_possible_shifts_left[worker_id].remove(shift)
                else:
                    counter += 1
            else:
                counter += 1

        improved_solutions.append(approved_solution)

    # the rest solutions get correct_overlap and optimization and mutation of one remove and one add
    for solution in solutions[5 * k:]:
        approved_solution = []

        workers_possible_shifts_left = copy.deepcopy(worker_possible_shifts_map)

        for item in solution:
            worker_id = item[0]
            shift_id = item[1]

            if shift_id in workers_possible_shifts_left[worker_id]:
                # add the legal shift
                approved_solution.append(item)

                # remove the overlap shifts from the remain possible shifts
                overlap_shifts = get_the_overlap_shifts(shift_id, workers_possible_shifts_left[worker_id])

                for shift in overlap_shifts:
                    if shift in workers_possible_shifts_left[worker_id]:
                        workers_possible_shifts_left[worker_id].remove(shift)

        # remove optimization
        counter = 0
        fitness = get_fitness(approved_solution)

        while counter < 2 and len(approved_solution) > 1:
            opt_solution = copy.deepcopy(approved_solution)
            # random remove
            index_to_remove = random.randint(0, len(opt_solution) - 1)
            opt_solution.pop(index_to_remove)
            new_fitness = get_fitness(opt_solution)

            if new_fitness < fitness:
                approved_solution = opt_solution
                # counter = 0
            else:
                counter += 1

        # add optimization
        counter = 0
        fitness = get_fitness(approved_solution)

        while counter < 2:
            opt_solution = copy.deepcopy(approved_solution)
            worker_id = random.choices(list(workers_map.keys()), k=1)
            worker_id = worker_id[0]

            if len(workers_possible_shifts_left[worker_id]):
                shift_id = random.choices(list(workers_possible_shifts_left[worker_id]), k=1)
                shift_id = shift_id[0]
                opt_solution.append((worker_id, shift_id))
                new_fitness = get_fitness(opt_solution)

                if new_fitness < fitness:
                    # counter = 0
                    approved_solution = opt_solution
                    # remove the overlap shifts from the remain possible shifts
                    overlap_shifts = get_the_overlap_shifts(shift_id, workers_possible_shifts_left[worker_id])
                    for shift in overlap_shifts:
                        if shift in workers_possible_shifts_left[worker_id]:
                            workers_possible_shifts_left[worker_id].remove(shift)
                else:
                    counter += 1
            else:
                counter += 1

        # mutation
        if random.uniform(0, 1) <= prob:
            # random remove
            if len(approved_solution) > 1:
                index_to_remove = random.randint(0, len(approved_solution) - 1)
                approved_solution.pop(index_to_remove)

            # random add
            worker_id = random.choices(list(workers_map.keys()), k=1)
            worker_id = worker_id[0]
            if len(workers_possible_shifts_left[worker_id]):
                shift_id = random.choices(list(workers_possible_shifts_left[worker_id]), k=1)
                shift_id = shift_id[0]
                approved_solution.append((worker_id, shift_id))

        improved_solutions.append(approved_solution)
    return improved_solutions


def find_next_generation(solutions):
    next_generation = []  # list of all solutions we pass to next generation
    crossover_population = []  # list of all solutions we pass to crossover function.
    fitness_array = get_fitness_array(solutions)  # list of fitness scores to all solutions

    lowest_fitness = fitness_array[0][1]  # save lowest fitness value
    # if generation % 10 == 0:  # display the lowest fitness permutation every 10 generations
    #     print("lowest_fitness prem: " + str(best_solution))

    index = fitness_array[0][0]  # save row of the ith best permutation from fitness array which contains tuples
    # of (row number,fitness score) of permutations
    solution = solutions[index]  # save the the ith best permutation from matrix
    best_solution = solution  # save lowest fitness permutation

    for i in range(5 * k):
        # the best 5*k permutations are passed as is to next generation and also copied and inserted 8 times  each
        # into the crossover population
        index = fitness_array[i][0]  # save row of the ith best permutation from fitness array which contains tuples
        # of (row number,fitness score) of permutations
        solution = solutions[index]  # save the the ith best permutation from matrix

        next_generation.append(solution)  # add permutation to next generation
        for j in range(8):  # do 8 times
            solution_cpy = copy.deepcopy(solution)
            crossover_population.append(solution_cpy)  # add permutation to crossover list
    for i in range(5 * k, 20 * k):
        # next 15*k best permutations are passed as is to next generation and also copied and inserted 4 times  each
        # into the crossover population
        index = fitness_array[i][0]
        solution = solutions[index]  # save the the ith best permutation from matrix
        next_generation.append(solution)  # add permutation to next generation
        for j in range(4):  # do 4 times
            solution_cpy = copy.deepcopy(solution)
            crossover_population.append(solution_cpy)  # add permutation to crossover list
    for i in range(20 * k, 25 * k):
        # the next 5*k best permutations are passed as is to next generation and to the crossover population
        index = fitness_array[i][0]
        solution = solutions[index]
        next_generation.append(solution)
        solution_cpy = copy.deepcopy(solution)
        crossover_population.append(solution_cpy)

    # next we create 15*k random permutation and pass them to next generation and crossover population in order to
    # create more variety
    random_solutions = generate_new_solutions(15 * k)
    next_generation += random_solutions
    random_copied_solution = copy.deepcopy(random_solutions)
    crossover_population += random_copied_solution

    next_generation += crossover(crossover_population)  # add crossover function output to next generation list

    # correct_overlap and optimization and mutation of one remove and one add
    next_generation = improve_solutions(next_generation, 0.5)

    return next_generation, lowest_fitness, best_solution, fitness_array


def get_evolution_solution(shifts, workers, requirements):
    """
    this is the regular main function of our program.
    It calls next generation function in a loop until algorithm convergence or generation 200.
    """
    global generation
    global shifts_list
    global requirements_list
    global workers_map

    shifts_list = shifts
    requirements_list = requirements
    workers_map = workers

    initialize()

    lowest_fitness = 100000
    counter = 0
    solutions = generate_new_solutions(100 * k)

    # continues until generation 200 or until lowest fitness doesn't change for 40 generations -- convergence
    while generation < 200 and counter <= 40:
        # call next generation function to find next generation
        solutions, current_lowest_fitness, lowest_fitness_prem, fitness_array = find_next_generation(solutions)
        # count the number of times the lowest fitness stays the same. used to find algorithm convergence
        if current_lowest_fitness != lowest_fitness:
            lowest_fitness = current_lowest_fitness
            counter = 0
        else:
            counter += 1

        generation += 1

    return solutions[0]


