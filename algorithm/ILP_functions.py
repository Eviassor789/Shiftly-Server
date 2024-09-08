import pulp
import random
import copy
from itertools import product
import json


def time_to_minutes(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m


def is_overlap(shift1, shift2):
    start1 = time_to_minutes(shift1['start_hour'])
    end1 = time_to_minutes(shift1['end_hour'])
    start2 = time_to_minutes(shift2['start_hour'])
    end2 = time_to_minutes(shift2['end_hour'])
    return (
            ((start2 <= start1 < end2) or
             (start2 < end1 <= end2) or
             (start1 <= start2 < end1) or
             (start1 < end2 <= end1)) and
            shift1['day'] == shift2['day']
    )


##########
# weight
# cost_weight = 0
# contracts_weight = 0
# requirements_weight = 0
# idle_workers_weight = 0

shifts_to_requirements_map = {}
possible_shifts_to_workers_map = {}
requirements_num_map = {}
worker_construct_map = {}
worker_possible_shifts_map = {}
relevant_shifts = {}


def json_print(data):
    result = {}
    for item in data:
        if item[1] not in result:
            result[item[1]] = []
        result[item[1]].append(item[0])

    return result


def convert_to_minutes(time):
    hours, minutes = map(int, time.split(":"))
    return hours * 60 + minutes


def duration_of_shift(my_shift_id):
    start = convert_to_minutes(relevant_shifts[my_shift_id]["start_hour"])
    end = convert_to_minutes(relevant_shifts[my_shift_id]["end_hour"])

    return (end - start) / 60


def is_hour_in_range(hour, start_hour, end_hour):
    # Convert hour, start_hour, and end_hour to integers for comparison
    hour_int = int(hour.replace(':', ''))
    start_hour_int = int(start_hour.replace(':', ''))
    end_hour_int = int(end_hour.replace(':', ''))

    # Check if the hour falls within the range
    return start_hour_int <= hour_int < end_hour_int


def get_relevant_requirements_for_shift(shift, requirements):
    requirements_array = []
    for requirement in requirements:
        if str(requirement['day']
        ) == str(shift['day']) \
                and requirement['profession'] == shift['profession'] \
                and is_hour_in_range(requirement['hour'], shift['start_hour'], shift['end_hour']):
            requirements_array.append(requirement)

    return requirements_array


def initialize(shifts, workers, requirements):
    # initialize the relevant_shifts_id
    for shift in shifts:
        for req in requirements:
            if req['profession'] == shift['profession'] and req['day'] == shift['day'] and is_hour_in_range(req['hour'],
                                                                                                            shift[
                                                                                                                'start_hour'],
                                                                                                            shift[
                                                                                                                'end_hour']):
                relevant_shifts[shift['id']] = shift
                break

    # for shift in shifts:
    #     relevant_shifts[shift['id']] = shift

    # initialize the relevant_shifts_id for every worker
    for worker_id, worker_info in workers.items():
        for shift in relevant_shifts.values():
            if shift['day'] in worker_info['days'] and shift['profession'] in worker_info['professions']:
                worker_info['relevant_shifts_id'].append(shift['id'])

    # initialize the shifts_to_workers_map
    for worker_id, worker_info in workers.items():
        for shift_id in worker_info["relevant_shifts_id"]:
            if shift_id not in possible_shifts_to_workers_map:
                possible_shifts_to_workers_map[shift_id] = []
            if worker_id not in possible_shifts_to_workers_map[shift_id]:
                possible_shifts_to_workers_map[shift_id].append(worker_id)

    # initialize the worker_construct_map
    for worker_id, worker_info in workers.items():
        worker_construct_map[worker_id] = worker_info['hours_per_week']

    # initialize the worker_possible_shifts_map
    for worker_id, worker_info in workers.items():
        worker_possible_shifts_map[worker_id] = worker_info['relevant_shifts_id']

    # initialize the shifts_to_requirements_map
    for shift in shifts:
        shifts_to_requirements_map[shift['id']] = get_relevant_requirements_for_shift(shift, requirements)

    # initialize the requirements_num_map
    for requirement in requirements:
        requirement_id = requirement['id']
        num = requirement['number']
        requirements_num_map[requirement_id] = num


def get_fitness_with_more_info(solution, shifts, workers, requirements):
    # the same as get fitness - but return also the cost, satisfied_contracts, satisfied_requirements, idle_workers
    initialize(shifts, workers, requirements)

    fitness = 0

    cost = 0
    satisfied_contracts = 0
    satisfied_requirements = 0
    idle_workers = 0
    total_requirements_num = 0

    shift_to_largest_req = {
        s['id']: max(
            req['number'] for req in requirements if req['profession'] == s['profession'] and req['day'] == s['day'] and
            time_to_minutes(s['start_hour']) <= time_to_minutes(req['hour']) < time_to_minutes(s['end_hour']))
        for s in shifts
        if any(req['profession'] == s['profession'] and req['day'] == s['day'] and
               time_to_minutes(s['start_hour']) <= time_to_minutes(req['hour']) < time_to_minutes(s['end_hour'])
               for req in requirements)
    }

    jsonSol = json_print(solution)
    for shift_id, workers_list in jsonSol.items():
        num_workers_in_shift = len(workers_list)
        idle_workers += max(0, num_workers_in_shift - shift_to_largest_req[shift_id])

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
        for requirement in get_relevant_requirements_for_shift(relevant_shifts[shift_id], requirements):
            requirement_id = requirement['id']
            if left_requirements_num_map[requirement_id]:
                left_requirements_num_map[requirement_id] -= 1
                idle_flag = False
        if idle_flag:
            idle_workers += 0

    # calculate satisfied_contracts
    for left_construct in constructs.values():
        if left_construct <= 0:
            satisfied_contracts += 1

    # calculate total_requirements_num
    for requirement in requirements:
        total_requirements_num += requirement['number']

    # calculate satisfied_requirements
    satisfied_requirements += total_requirements_num
    for num in left_requirements_num_map.values():
        satisfied_requirements -= num

    # lower fitness is better fitness
    # fitness += cost * cost_weight
    # fitness += idle_workers * idle_workers_weight
    # fitness -= satisfied_contracts * contracts_weight
    # fitness -= satisfied_requirements * requirements_weight

    return cost, satisfied_contracts, satisfied_requirements, idle_workers, total_requirements_num


def find_solution(shifts, workers, requirements, idle_constrain, contracts_constrain, state):
    # Define the weights
    idle_workers_weight = 0
    contracts_weight = 0
    cost_weight = 0
    requirements_weight = 0


    for shift in shifts:
        shifts_to_requirements_map[shift['id']] = get_relevant_requirements_for_shift(shift, requirements)

    # ILP Model
    model = pulp.LpProblem("Optimize_Scheduling", pulp.LpMaximize)

    # Variables: Binary decision variables for worker assignments to shifts
    assignments = pulp.LpVariable.dicts("Assignment",
                                        ((workers[w]['id'], s['id']) for w in workers for s in shifts),
                                        cat='Binary')

    # Constraint 1: Workers can only be assigned to shifts they are eligible for
    for w in workers:
        for s in shifts:
            if s['profession'] not in workers[w]['professions'] or s['day'] not in workers[w]['days']:
                model += assignments[(workers[w]['id'], s['id'])] == 0

    # Constraint 2: Workers cannot work overlapping shifts
    for w in workers:
        for s1 in shifts:
            for s2 in shifts:
                if s1 != s2 and is_overlap(s1, s2):
                    model += assignments[(workers[w]['id'], s1['id'])] + assignments[(workers[w]['id'], s2['id'])] <= 1

    # Constraint 3: Workers cannot work in non-relevant shifts
    for s in shifts:
        # Check if there are any requirements overlapping with the shift
        has_requirements = any(req['profession'] == s['profession'] and
                               req['day'] == s['day'] and
                               time_to_minutes(s['start_hour']) <= time_to_minutes(req['hour']) < time_to_minutes(
            s['end_hour'])
                               for req in requirements)

        if not has_requirements:
            # Add a constraint to ensure the shift is left empty
            for w in workers:
                model += assignments[workers[w]['id'], s['id']] == 0

    # Calculate total cost
    total_cost = pulp.lpSum(assignments[(workers[w]['id'], s['id'])] * s['cost'] for w in workers for s in shifts)

    # Calculate the number of satisfied contracts
    satisfied_contracts = pulp.lpSum(pulp.lpSum(
        assignments[(workers[w]['id'], s['id'])] * (
                time_to_minutes(s['end_hour']) - time_to_minutes(s['start_hour'])) / 60
        for s in shifts) >= workers[w]['hours_per_week'] for w in workers)

    if idle_constrain:
        for w in workers:
            model += pulp.lpSum(
                assignments[(workers[w]['id'], s['id'])] * (
                        time_to_minutes(s['end_hour']) - time_to_minutes(s['start_hour'])) / 60
                for s in shifts
            ) >= workers[w]['hours_per_week']

    if contracts_constrain:
        for w in workers:
            total_worked_hours = sum(
                assignments[(w, s['id'])] * (time_to_minutes(s['end_hour']) - time_to_minutes(s['start_hour'])) / 60
                for s in shifts)
            model += total_worked_hours >= workers[w]['hours_per_week']

    shift_to_largest_req = {
        s['id']: max(
            req['number'] for req in requirements if req['profession'] == s['profession'] and req['day'] == s['day'] and
            time_to_minutes(s['start_hour']) <= time_to_minutes(req['hour']) < time_to_minutes(s['end_hour']))
        for s in shifts
        if any(req['profession'] == s['profession'] and req['day'] == s['day'] and
               time_to_minutes(s['start_hour']) <= time_to_minutes(req['hour']) < time_to_minutes(s['end_hour'])
               for req in requirements)
    }

    # Calculate the number of idle workers based on the largest requirement for each shift
    idle_workers_vars = pulp.LpVariable.dicts("idle_workers", ((s['id']) for s in shifts), lowBound=0, cat='Integer')

    for s in shifts:
        if any(req['profession'] == s['profession'] and req['day'] == s['day'] and
               time_to_minutes(s['start_hour']) <= time_to_minutes(req['hour']) < time_to_minutes(s['end_hour'])
               for req in requirements):
            workers_num = pulp.lpSum(assignments[(workers[w]['id'], s['id'])] for w in workers)
            model += idle_workers_vars[(s['id'])] >= workers_num - shift_to_largest_req[s['id']]
            model += idle_workers_vars[(s['id'])] >= 0

    idle_workers = pulp.lpSum(idle_workers_vars[(s['id'])] for s in shifts)

    # Objective: Weighted sum of the objectives

    if state == 1:
        idle_workers_weight = 1000000
        contracts_weight = 10000
        requirements_weight = 100
        cost_weight = 10


        if contracts_constrain:
            model += (requirements_weight * pulp.lpSum(
                assignments[(workers[w]['id'], s['id'])]*len(shifts_to_requirements_map[s['id']]) for w in workers for s in shifts)
                      - cost_weight * total_cost
                      ), "Optimize Objectives"

        elif idle_constrain:
            model += (
                             contracts_weight * satisfied_contracts
                             + requirements_weight * pulp.lpSum(
                         assignments[(workers[w]['id'], s['id'])]*len(shifts_to_requirements_map[s['id']]) for w in workers for s in shifts)
                             - cost_weight * total_cost
                     ), "Optimize Objectives"
        else:
            model += (
                             contracts_weight * satisfied_contracts
                             + requirements_weight * pulp.lpSum(
                         assignments[(workers[w]['id'], s['id'])]*len(shifts_to_requirements_map[s['id']]) for w in workers for s in shifts)
                             - cost_weight * total_cost
                             - idle_workers_weight * idle_workers
                     ), "Optimize Objectives"

    if state == 2:
        idle_workers_weight = 1000000
        contracts_weight = 10000
        requirements_weight = 0
        cost_weight = 1000

        if contracts_constrain:
            model += (

                             - cost_weight * total_cost
                     ), "Optimize Objectives"

        elif idle_constrain:
            model += (
                             contracts_weight * satisfied_contracts
                            - cost_weight * total_cost
                     ), "Optimize Objectives"

        else:
            model += (
                             contracts_weight * satisfied_contracts
                             - cost_weight * total_cost
                             - idle_workers_weight * idle_workers
                     ), "Optimize Objectives"

    if state == 3:
        idle_workers_weight = 10000
        contracts_weight = 1000000
        requirements_weight = 100
        cost_weight = 10

        if idle_constrain:
            model += (
                             requirements_weight * pulp.lpSum(
                         assignments[(workers[w]['id'], s['id'])]*len(shifts_to_requirements_map[s['id']]) for w in workers for s in shifts)
                             - cost_weight * total_cost
                     ), "Optimize Objectives"


        elif contracts_constrain:
            model += (
                             requirements_weight * pulp.lpSum(
                         assignments[(workers[w]['id'], s['id'])]*len(shifts_to_requirements_map[s['id']]) for w in workers for s in shifts)
                             - cost_weight * total_cost
                             - idle_workers_weight * idle_workers
                     ), "Optimize Objectives"

        else:
            model += (
                             contracts_weight * satisfied_contracts
                             + requirements_weight * pulp.lpSum(
                         assignments[(workers[w]['id'], s['id'])]*len(shifts_to_requirements_map[s['id']]) for w in workers for s in shifts)
                             - cost_weight * total_cost
                             - idle_workers_weight * idle_workers
                     ), "Optimize Objectives"

    if state == 4:
        idle_workers_weight = 10000
        contracts_weight = 1000000
        requirements_weight = 0
        cost_weight = 1000

        if idle_constrain:
            model += (
                            - cost_weight * total_cost
                     ), "Optimize Objectives"


        elif contracts_constrain:
            model += (
                             - cost_weight * total_cost
                             - idle_workers_weight * idle_workers
                     ), "Optimize Objectives"

        else:
            model += (
                             contracts_weight * satisfied_contracts
                             - cost_weight * total_cost
                             - idle_workers_weight * idle_workers
                     ), "Optimize Objectives"

    # model += (
    #                  contracts_weight * satisfied_contracts
    #                  + requirements_weight * pulp.lpSum(
    #              assignments[(workers[w]['id'], s['id'])] for w in workers for s in shifts)
    #                  - cost_weight * total_cost
    #                  - idle_workers_weight * idle_workers
    #          ), "Optimize Objectives"

    # Solve the model
    model.solve(pulp.PULP_CBC_CMD(msg=False))

    # Output the results
    print("Status:", pulp.LpStatus[model.status])
    # for w in workers:
    #     for s in shifts:
    #         if pulp.value(assignments[(workers[w]['id'], s['id'])]) == 1:
    #             print(f"Worker {workers[w]['id']} is assigned to Shift {s['id']}")

    # Extract the solution
    solution = [(w_id, s_id) for (w_id, s_id), var in assignments.items() if pulp.value(var) == 1]
    solution = sorted(solution, key=lambda x: x[1])
    status = pulp.LpStatus[model.status]

    return solution, status
