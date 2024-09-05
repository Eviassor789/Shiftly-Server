import pulp
import random
import copy
from itertools import product
import json
from ILP_functions import time_to_minutes, is_overlap, find_solution, get_fitness_with_more_info, json_print
from collections import defaultdict
from datetime import datetime, timedelta
from evolutionAlg import get_evolution_solution


def time_to_minutes(time_str):
    """Convert HH:MM time string to minutes since midnight."""
    time_obj = datetime.strptime(time_str, '%H:%M')
    return time_obj.hour * 60 + time_obj.minute


def minutes_to_time(minutes):
    """Convert minutes since midnight back to HH:MM time string."""
    hours = minutes // 60
    minutes = minutes % 60
    return f"{hours:02d}:{minutes:02d}"


def process_requirements(requirements):
    hourly_requirements = defaultdict(int)

    for req in requirements:
        profession = req['profession']
        day = req['day']
        start_minutes = time_to_minutes(req['start_hour'])
        end_minutes = time_to_minutes(req['end_hour'])
        number = req['number']

        # Go through each hour in the range and add the number of workers required
        current_time = start_minutes
        while current_time < end_minutes:
            hourly_requirements[(profession, day, minutes_to_time(current_time))] += number
            current_time += 60  # move to the next hour

    # Convert the result into the desired format
    result = []
    req_id = 1
    for (profession, day, hour), number in sorted(hourly_requirements.items()):
        result.append({'id': req_id, 'profession': profession, 'day': day, 'hour': hour, 'number': number})
        req_id += 1

    return result


def get_assignment(shifts, workers, format_requirements, contracts_obj, cost_obj):
    requirements = process_requirements(format_requirements)

    # states:
    # 1 : idle-req
    # 2 : idle-cost
    # 3 : contracts-req
    # 4 : contracts-cost
    # def find_solution(shifts, workers, requirements, idle_constrain, contracts_constrain, state)

    state = 0
    if contracts_obj:
        if cost_obj:
            state = 4
        else:
            state = 3
    else:
        if cost_obj:
            state = 2
        else:
            state = 1




    if state == 1:
        solution, status = find_solution(shifts, workers, requirements, True, True, 1)
        if status == "Optimal":
            cost, satisfied_contracts, satisfied_requirements, idle_workers, total_requirement_num = get_fitness_with_more_info(
                solution, shifts, workers, requirements)
            print("True, True, 1: ")
            print("solution: " + str(solution))
            print("json: " + str(json_print(solution)))
            print("cost: " + str(cost))
            print("satisfied_contracts: " + str(satisfied_contracts) + ' / ' + str(len(workers)))
            print("satisfied_requirements: " + str(satisfied_requirements) + ' / ' + str(total_requirement_num))
            print("idle_workers: " + str(idle_workers))
            print()

            return solution
        else:
            solution, status = find_solution(shifts, workers, requirements, True, False, 1)
            if status == "Optimal":
                cost, satisfied_contracts, satisfied_requirements, idle_workers, total_requirement_num = get_fitness_with_more_info(
                    solution, shifts, workers, requirements)
                print("True, False, 1: ")
                print("solution: " + str(solution))
                print("json: " + str(json_print(solution)))
                print("cost: " + str(cost))
                print("satisfied_contracts: " + str(satisfied_contracts) + ' / ' + str(len(workers)))
                print("satisfied_requirements: " + str(satisfied_requirements) + ' / ' + str(total_requirement_num))
                print("idle_workers: " + str(idle_workers))
                print()

                return solution
            else:
                solution, status = find_solution(shifts, workers, requirements, False, False, 1)
                if status == "Optimal":
                    cost, satisfied_contracts, satisfied_requirements, idle_workers, total_requirement_num = get_fitness_with_more_info(
                        solution, shifts, workers, requirements)
                    print("False, False, 1: ")
                    print("solution: " + str(solution))
                    print("json: " + str(json_print(solution)))
                    print("cost: " + str(cost))
                    print("satisfied_contracts: " + str(satisfied_contracts) + ' / ' + str(len(workers)))
                    print("satisfied_requirements: " + str(satisfied_requirements) + ' / ' + str(total_requirement_num))
                    print("idle_workers: " + str(idle_workers))
                    print()

                    return solution
                else:
                    return get_evolution_solution(shifts, workers, requirements)

##########################################################

    if state == 2:
        solution, status = find_solution(shifts, workers, requirements, True, True, 2)
        if status == "Optimal":
            cost, satisfied_contracts, satisfied_requirements, idle_workers, total_requirement_num = get_fitness_with_more_info(
                solution, shifts, workers, requirements)
            print("True, True, 2: ")
            print("solution: " + str(solution))
            print("json: " + str(json_print(solution)))
            print("cost: " + str(cost))
            print("satisfied_contracts: " + str(satisfied_contracts) + ' / ' + str(len(workers)))
            print("satisfied_requirements: " + str(satisfied_requirements) + ' / ' + str(total_requirement_num))
            print("idle_workers: " + str(idle_workers))
            print()

            return solution
        else:
            solution, status = find_solution(shifts, workers, requirements, True, False, 2)
            if status == "Optimal":
                cost, satisfied_contracts, satisfied_requirements, idle_workers, total_requirement_num = get_fitness_with_more_info(
                    solution, shifts, workers, requirements)
                print("True, False, 2: ")
                print("solution: " + str(solution))
                print("json: " + str(json_print(solution)))
                print("cost: " + str(cost))
                print("satisfied_contracts: " + str(satisfied_contracts) + ' / ' + str(len(workers)))
                print("satisfied_requirements: " + str(satisfied_requirements) + ' / ' + str(total_requirement_num))
                print("idle_workers: " + str(idle_workers))
                print()

                return solution
            else:
                solution, status = find_solution(shifts, workers, requirements, False, False, 2)
                if status == "Optimal":
                    cost, satisfied_contracts, satisfied_requirements, idle_workers, total_requirement_num = get_fitness_with_more_info(
                        solution, shifts, workers, requirements)
                    print("False, False, 2: ")
                    print("solution: " + str(solution))
                    print("json: " + str(json_print(solution)))
                    print("cost: " + str(cost))
                    print("satisfied_contracts: " + str(satisfied_contracts) + ' / ' + str(len(workers)))
                    print("satisfied_requirements: " + str(satisfied_requirements) + ' / ' + str(total_requirement_num))
                    print("idle_workers: " + str(idle_workers))
                    print()

                    return solution
                else:
                    return get_evolution_solution(shifts, workers, requirements)


#########################################################

    if state == 3:
        solution, status = find_solution(shifts, workers, requirements, True, True, 3)
        if status == "Optimal":
            cost, satisfied_contracts, satisfied_requirements, idle_workers, total_requirement_num = get_fitness_with_more_info(
                solution, shifts, workers, requirements)
            print("True, True, 3: ")
            print("solution: " + str(solution))
            print("json: " + str(json_print(solution)))
            print("cost: " + str(cost))
            print("satisfied_contracts: " + str(satisfied_contracts) + ' / ' + str(len(workers)))
            print("satisfied_requirements: " + str(satisfied_requirements) + ' / ' + str(total_requirement_num))
            print("idle_workers: " + str(idle_workers))
            print()

            return solution
        else:
            solution, status = find_solution(shifts, workers, requirements, False, True, 3)
            if status == "Optimal":
                cost, satisfied_contracts, satisfied_requirements, idle_workers, total_requirement_num = get_fitness_with_more_info(
                    solution, shifts, workers, requirements)
                print("False, True, 3: ")
                print("solution: " + str(solution))
                print("json: " + str(json_print(solution)))
                print("cost: " + str(cost))
                print("satisfied_contracts: " + str(satisfied_contracts) + ' / ' + str(len(workers)))
                print("satisfied_requirements: " + str(satisfied_requirements) + ' / ' + str(total_requirement_num))
                print("idle_workers: " + str(idle_workers))
                print()

                return solution
            else:
                solution, status = find_solution(shifts, workers, requirements, False, False, 3)
                if status == "Optimal":
                    cost, satisfied_contracts, satisfied_requirements, idle_workers, total_requirement_num = get_fitness_with_more_info(
                        solution, shifts, workers, requirements)
                    print("False, False, 3: ")
                    print("solution: " + str(solution))
                    print("json: " + str(json_print(solution)))
                    print("cost: " + str(cost))
                    print("satisfied_contracts: " + str(satisfied_contracts) + ' / ' + str(len(workers)))
                    print("satisfied_requirements: " + str(satisfied_requirements) + ' / ' + str(total_requirement_num))
                    print("idle_workers: " + str(idle_workers))
                    print()

                    return solution
                else:
                    return get_evolution_solution(shifts, workers, requirements)

#################################################################

    if state == 4:
        solution, status = find_solution(shifts, workers, requirements, True, True, 4)
        if status == "Optimal":
            cost, satisfied_contracts, satisfied_requirements, idle_workers, total_requirement_num = get_fitness_with_more_info(
                solution, shifts, workers, requirements)
            print("True, True, 4: ")
            print("solution: " + str(solution))
            print("json: " + str(json_print(solution)))
            print("cost: " + str(cost))
            print("satisfied_contracts: " + str(satisfied_contracts) + ' / ' + str(len(workers)))
            print("satisfied_requirements: " + str(satisfied_requirements) + ' / ' + str(total_requirement_num))
            print("idle_workers: " + str(idle_workers))
            print()

            return solution
        else:
            solution, status = find_solution(shifts, workers, requirements, False, True, 4)
            if status == "Optimal":
                cost, satisfied_contracts, satisfied_requirements, idle_workers, total_requirement_num = get_fitness_with_more_info(
                    solution, shifts, workers, requirements)
                print("False, True, 4: ")
                print("solution: " + str(solution))
                print("json: " + str(json_print(solution)))
                print("cost: " + str(cost))
                print("satisfied_contracts: " + str(satisfied_contracts) + ' / ' + str(len(workers)))
                print("satisfied_requirements: " + str(satisfied_requirements) + ' / ' + str(total_requirement_num))
                print("idle_workers: " + str(idle_workers))
                print()

                return solution
            else:
                solution, status = find_solution(shifts, workers, requirements, False, False, 4)
                if status == "Optimal":
                    cost, satisfied_contracts, satisfied_requirements, idle_workers, total_requirement_num = get_fitness_with_more_info(
                        solution, shifts, workers, requirements)
                    print("False, False, 4: ")
                    print("solution: " + str(solution))
                    print("json: " + str(json_print(solution)))
                    print("cost: " + str(cost))
                    print("satisfied_contracts: " + str(satisfied_contracts) + ' / ' + str(len(workers)))
                    print("satisfied_requirements: " + str(satisfied_requirements) + ' / ' + str(total_requirement_num))
                    print("idle_workers: " + str(idle_workers))
                    print()

                    return solution
                else:
                    return get_evolution_solution(shifts, workers, requirements)

    return None


# Example data
shifts = [{'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '12:00', 'end_hour': '17:00', 'cost': 80}, {'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '15:00', 'end_hour': '20:00', 'cost': 80}, {'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '14:00', 'end_hour': '17:00', 'cost': 60}, {'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '15:00', 'end_hour': '18:00', 'cost': 60}, {'profession': 'Doctor', 'day': 'Monday', 'start_hour': '08:00', 'end_hour': '13:00', 'cost': 80}, {'profession': 'Doctor', 'day': 'Monday', 'start_hour': '10:00', 'end_hour': '13:00', 'cost': 60}, {'profession': 'Doctor', 'day': 'Monday', 'start_hour': '10:00', 'end_hour': '15:00', 'cost': 80}, {'profession': 'Doctor', 'day': 'Monday', 'start_hour': '11:00', 'end_hour': '14:00', 'cost': 60}, {'profession': 'Doctor', 'day': 'Tuesday', 'start_hour': '07:00', 'end_hour': '12:00', 'cost': 80}, {'profession': 'Doctor', 'day': 'Tuesday', 'start_hour': '12:00', 'end_hour': '17:00', 'cost': 80}, {'profession': 'Doctor', 'day': 'Tuesday', 'start_hour': '10:00', 'end_hour': '15:00', 'cost': 80}, {'profession': 'Doctor', 'day': 'Tuesday', 'start_hour': '08:00', 'end_hour': '11:00', 'cost': 60}, {'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '07:00', 'end_hour': '10:00', 'cost': 60}, {'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '07:00', 'end_hour': '10:00', 'cost': 60}, {'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '09:00', 'end_hour': '12:00', 'cost': 60}, {'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '13:00', 'end_hour': '18:00', 'cost': 80}, {'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '13:00', 'end_hour': '18:00', 'cost': 80}, {'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '08:00', 'end_hour': '11:00', 'cost': 60}, {'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '10:00', 'end_hour': '15:00', 'cost': 80}, {'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '14:00', 'end_hour': '17:00', 'cost': 60}, {'profession': 'Doctor', 'day': 'Friday', 'start_hour': '15:00', 'end_hour': '20:00', 'cost': 80}, {'profession': 'Doctor', 'day': 'Friday', 'start_hour': '08:00', 'end_hour': '13:00', 'cost': 80}, {'profession': 'Doctor', 'day': 'Friday', 'start_hour': '08:00', 'end_hour': '11:00', 'cost': 60}, {'profession': 'Doctor', 'day': 'Friday', 'start_hour': '14:00', 'end_hour': '17:00', 'cost': 60}, {'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '08:00', 'end_hour': '13:00', 'cost': 80}, {'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '07:00', 'end_hour': '10:00', 'cost': 60}, {'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '09:00', 'end_hour': '14:00', 'cost': 80}, {'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '07:00', 'end_hour': '12:00', 'cost': 80}, {'profession': 'Teacher', 'day': 'Monday', 'start_hour': '11:00', 'end_hour': '16:00', 'cost': 80}, {'profession': 'Teacher', 'day': 'Monday', 'start_hour': '12:00', 'end_hour': '17:00', 'cost': 80}, {'profession': 'Teacher', 'day': 'Monday', 'start_hour': '09:00', 'end_hour': '14:00', 'cost': 80}, {'profession': 'Teacher', 'day': 'Monday', 'start_hour': '15:00', 'end_hour': '18:00', 'cost': 60}, {'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '15:00', 'end_hour': '18:00', 'cost': 60}, {'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '09:00', 'end_hour': '12:00', 'cost': 60}, {'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '12:00', 'end_hour': '17:00', 'cost': 80}, {'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '08:00', 'end_hour': '11:00', 'cost': 60}, {'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '13:00', 'end_hour': '18:00', 'cost': 80}, {'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '15:00', 'end_hour': '18:00', 'cost': 60}, {'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '12:00', 'end_hour': '15:00', 'cost': 60}, {'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '11:00', 'end_hour': '16:00', 'cost': 80}, {'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '07:00', 'end_hour': '10:00', 'cost': 60}, {'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '08:00', 'end_hour': '13:00', 'cost': 80}, {'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '12:00', 'end_hour': '15:00', 'cost': 60}, {'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '12:00', 'end_hour': '15:00', 'cost': 60}, {'profession': 'Teacher', 'day': 'Friday', 'start_hour': '12:00', 'end_hour': '15:00', 'cost': 60}, {'profession': 'Teacher', 'day': 'Friday', 'start_hour': '09:00', 'end_hour': '12:00', 'cost': 60}, {'profession': 'Teacher', 'day': 'Friday', 'start_hour': '12:00', 'end_hour': '17:00', 'cost': 80}, {'profession': 'Teacher', 'day': 'Friday', 'start_hour': '14:00', 'end_hour': '19:00', 'cost': 80}, {'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '08:00', 'end_hour': '11:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '12:00', 'end_hour': '17:00', 'cost': 80}, {'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '10:00', 'end_hour': '13:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '08:00', 'end_hour': '11:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Monday', 'start_hour': '15:00', 'end_hour': '18:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Monday', 'start_hour': '08:00', 'end_hour': '11:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Monday', 'start_hour': '15:00', 'end_hour': '18:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Monday', 'start_hour': '15:00', 'end_hour': '20:00', 'cost': 80}, {'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '07:00', 'end_hour': '12:00', 'cost': 80}, {'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '11:00', 'end_hour': '14:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '07:00', 'end_hour': '10:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '12:00', 'end_hour': '15:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '14:00', 'end_hour': '17:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '14:00', 'end_hour': '17:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '08:00', 'end_hour': '11:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '08:00', 'end_hour': '13:00', 'cost': 80}, {'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '15:00', 'end_hour': '18:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '08:00', 'end_hour': '13:00', 'cost': 80}, {'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '15:00', 'end_hour': '18:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '09:00', 'end_hour': '12:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Friday', 'start_hour': '07:00', 'end_hour': '10:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Friday', 'start_hour': '10:00', 'end_hour': '13:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Friday', 'start_hour': '15:00', 'end_hour': '20:00', 'cost': 80}, {'profession': 'Nurse', 'day': 'Friday', 'start_hour': '14:00', 'end_hour': '17:00', 'cost': 60}, {'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '07:00', 'end_hour': '12:00', 'cost': 80}, {'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '11:00', 'end_hour': '14:00', 'cost': 60}, {'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '11:00', 'end_hour': '14:00', 'cost': 60}, {'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '13:00', 'end_hour': '16:00', 'cost': 60}, {'profession': 'Engineer', 'day': 'Monday', 'start_hour': '13:00', 'end_hour': '16:00', 'cost': 60}, {'profession': 'Engineer', 'day': 'Monday', 'start_hour': '12:00', 'end_hour': '15:00', 'cost': 60}, {'profession': 'Engineer', 'day': 'Monday', 'start_hour': '11:00', 'end_hour': '16:00', 'cost': 80}, {'profession': 'Engineer', 'day': 'Monday', 'start_hour': '10:00', 'end_hour': '15:00', 'cost': 80}, {'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '14:00', 'end_hour': '17:00', 'cost': 60}, {'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '10:00', 'end_hour': '15:00', 'cost': 80}, {'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '09:00', 'end_hour': '14:00', 'cost': 80}, {'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '09:00', 'end_hour': '12:00', 'cost': 60}, {'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '15:00', 'end_hour': '20:00', 'cost': 80}, {'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '11:00', 'end_hour': '16:00', 'cost': 80}, {'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '09:00', 'end_hour': '14:00', 'cost': 80}, {'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '14:00', 'end_hour': '19:00', 'cost': 80}, {'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '14:00', 'end_hour': '19:00', 'cost': 80}, {'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '12:00', 'end_hour': '15:00', 'cost': 60}, {'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '09:00', 'end_hour': '14:00', 'cost': 80}, {'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '14:00', 'end_hour': '17:00', 'cost': 60}, {'profession': 'Engineer', 'day': 'Friday', 'start_hour': '15:00', 'end_hour': '20:00', 'cost': 80}, {'profession': 'Engineer', 'day': 'Friday', 'start_hour': '10:00', 'end_hour': '15:00', 'cost': 80}, {'profession': 'Engineer', 'day': 'Friday', 'start_hour': '07:00', 'end_hour': '10:00', 'cost': 60}, {'profession': 'Engineer', 'day': 'Friday', 'start_hour': '15:00', 'end_hour': '18:00', 'cost': 60}]

workers = {0: {'id': 0, 'name': '_0', 'professions': ['Nurse', 'Engineer'], 'days': ['Friday', 'Sunday', 'Wednesday', 'Monday', 'Thursday', 'Tuesday'], 'relevant_shifts_id': [], 'hours_per_week': 7}, 1: {'id': 1, 'name': '_1', 'professions': ['Doctor', 'Teacher', 'Engineer', 'Nurse'], 'days': ['Friday', 'Thursday', 'Monday', 'Wednesday', 'Tuesday'], 'relevant_shifts_id': [], 'hours_per_week': 5}, 2: {'id': 2, 'name': '_2', 'professions': ['Engineer', 'Teacher', 'Doctor', 'Nurse'], 'days': ['Thursday', 'Sunday', 'Friday', 'Wednesday', 'Tuesday'], 'relevant_shifts_id': [], 'hours_per_week': 8}, 3: {'id': 3, 'name': '_3', 'professions': ['Teacher', 'Doctor', 'Engineer'], 'days': ['Monday', 'Friday', 'Tuesday', 'Thursday', 'Sunday', 'Wednesday'], 'relevant_shifts_id': [], 'hours_per_week': 11}, 4: {'id': 4, 'name': '_4', 'professions': ['Engineer', 'Teacher', 'Nurse', 'Doctor'], 'days': ['Sunday', 'Monday', 'Thursday', 'Wednesday', 'Friday', 'Tuesday'], 'relevant_shifts_id': [], 'hours_per_week': 8}, 5: {'id': 5, 'name': '_5', 'professions': ['Nurse', 'Engineer'], 'days': ['Sunday', 'Tuesday', 'Monday', 'Wednesday', 'Thursday', 'Friday'], 'relevant_shifts_id': [], 'hours_per_week': 7}, 6: {'id': 6, 'name': '_6', 'professions': ['Nurse', 'Doctor', 'Teacher'], 'days': ['Tuesday', 'Sunday', 'Thursday', 'Friday', 'Monday', 'Wednesday'], 'relevant_shifts_id': [], 'hours_per_week': 11}, 7: {'id': 7, 'name': '_7', 'professions': ['Engineer', 'Nurse'], 'days': ['Sunday', 'Wednesday', 'Friday', 'Thursday', 'Monday'], 'relevant_shifts_id': [], 'hours_per_week': 11}, 8: {'id': 8, 'name': '_8', 'professions': ['Teacher', 'Engineer', 'Doctor'], 'days': ['Tuesday', 'Monday', 'Sunday', 'Thursday', 'Friday'], 'relevant_shifts_id': [], 'hours_per_week': 7}, 9: {'id': 9, 'name': '_9', 'professions': ['Nurse', 'Doctor'], 'days': ['Tuesday', 'Wednesday', 'Monday', 'Thursday', 'Friday'], 'relevant_shifts_id': [], 'hours_per_week': 18}, 10: {'id': 10, 'name': '_10', 'professions': ['Engineer', 'Nurse', 'Doctor'], 'days': ['Sunday', 'Friday', 'Monday', 'Wednesday'], 'relevant_shifts_id': [], 'hours_per_week': 8}, 11: {'id': 11, 'name': '_11', 'professions': ['Doctor', 'Teacher', 'Engineer'], 'days': ['Wednesday', 'Sunday', 'Friday', 'Thursday'], 'relevant_shifts_id': [], 'hours_per_week': 6}, 12: {'id': 12, 'name': '_12', 'professions': ['Engineer', 'Doctor', 'Nurse', 'Teacher'], 'days': ['Wednesday', 'Sunday', 'Monday', 'Friday'], 'relevant_shifts_id': [], 'hours_per_week': 6}, 13: {'id': 13, 'name': '_13', 'professions': ['Doctor', 'Engineer', 'Nurse', 'Teacher'], 'days': ['Friday', 'Thursday', 'Tuesday', 'Sunday', 'Wednesday', 'Monday'], 'relevant_shifts_id': [], 'hours_per_week': 10}, 14: {'id': 14, 'name': '_14', 'professions': ['Engineer', 'Nurse'], 'days': ['Thursday', 'Monday', 'Tuesday', 'Wednesday', 'Sunday', 'Friday'], 'relevant_shifts_id': [], 'hours_per_week': 6}, 15: {'id': 15, 'name': '_15', 'professions': ['Doctor', 'Teacher', 'Nurse'], 'days': ['Tuesday', 'Monday', 'Thursday', 'Friday'], 'relevant_shifts_id': [], 'hours_per_week': 13}, 16: {'id': 16, 'name': '_16', 'professions': ['Teacher', 'Nurse', 'Doctor', 'Engineer'], 'days': ['Tuesday', 'Thursday', 'Friday', 'Monday'], 'relevant_shifts_id': [], 'hours_per_week': 13}, 17: {'id': 17, 'name': '_17', 'professions': ['Engineer', 'Doctor', 'Teacher', 'Nurse'], 'days': ['Thursday', 'Tuesday', 'Sunday', 'Wednesday'], 'relevant_shifts_id': [], 'hours_per_week': 14}, 18: {'id': 18, 'name': '_18', 'professions': ['Nurse', 'Teacher', 'Doctor'], 'days': ['Wednesday', 'Sunday', 'Thursday', 'Tuesday', 'Friday'], 'relevant_shifts_id': [], 'hours_per_week': 5}, 19: {'id': 19, 'name': '_19', 'professions': ['Engineer', 'Teacher', 'Doctor'], 'days': ['Wednesday', 'Tuesday', 'Monday', 'Thursday', 'Sunday', 'Friday'], 'relevant_shifts_id': [], 'hours_per_week': 14}}

format_requirements = [{'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '13:00', 'end_hour': '14:00', 'number': 6}, {'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '15:00', 'end_hour': '19:00', 'number': 8}, {'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '13:00', 'end_hour': '14:00', 'number': 8}, {'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '12:00', 'end_hour': '16:00', 'number': 8}, {'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '17:00', 'end_hour': '18:00', 'number': 3}, {'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '10:00', 'end_hour': '14:00', 'number': 8}, {'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 7}, {'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 3}, {'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '17:00', 'end_hour': '18:00', 'number': 6}, {'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '12:00', 'end_hour': '16:00', 'number': 6}, {'profession': 'Doctor', 'day': 'Monday', 'start_hour': '10:00', 'end_hour': '11:00', 'number': 5}, {'profession': 'Doctor', 'day': 'Monday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 8}, {'profession': 'Doctor', 'day': 'Monday', 'start_hour': '15:00', 'end_hour': '19:00', 'number': 7}, {'profession': 'Doctor', 'day': 'Monday', 'start_hour': '07:00', 'end_hour': '08:00', 'number': 8}, {'profession': 'Doctor', 'day': 'Monday', 'start_hour': '07:00', 'end_hour': '08:00', 'number': 7}, {'profession': 'Doctor', 'day': 'Monday', 'start_hour': '14:00', 'end_hour': '15:00', 'number': 6}, {'profession': 'Doctor', 'day': 'Monday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 3}, {'profession': 'Doctor', 'day': 'Monday', 'start_hour': '16:00', 'end_hour': '17:00', 'number': 4}, {'profession': 'Doctor', 'day': 'Monday', 'start_hour': '12:00', 'end_hour': '16:00', 'number': 8}, {'profession': 'Doctor', 'day': 'Monday', 'start_hour': '10:00', 'end_hour': '11:00', 'number': 3}, {'profession': 'Doctor', 'day': 'Tuesday', 'start_hour': '13:00', 'end_hour': '14:00', 'number': 8}, {'profession': 'Doctor', 'day': 'Tuesday', 'start_hour': '07:00', 'end_hour': '08:00', 'number': 6}, {'profession': 'Doctor', 'day': 'Tuesday', 'start_hour': '10:00', 'end_hour': '11:00', 'number': 7}, {'profession': 'Doctor', 'day': 'Tuesday', 'start_hour': '17:00', 'end_hour': '21:00', 'number': 7}, {'profession': 'Doctor', 'day': 'Tuesday', 'start_hour': '16:00', 'end_hour': '20:00', 'number': 6}, {'profession': 'Doctor', 'day': 'Tuesday', 'start_hour': '11:00', 'end_hour': '15:00', 'number': 4}, {'profession': 'Doctor', 'day': 'Tuesday', 'start_hour': '15:00', 'end_hour': '16:00', 'number': 3}, {'profession': 'Doctor', 'day': 'Tuesday', 'start_hour': '09:00', 'end_hour': '10:00', 'number': 4}, {'profession': 'Doctor', 'day': 'Tuesday', 'start_hour': '16:00', 'end_hour': '17:00', 'number': 8}, {'profession': 'Doctor', 'day': 'Tuesday', 'start_hour': '12:00', 'end_hour': '13:00', 'number': 3}, {'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '12:00', 'end_hour': '13:00', 'number': 4}, {'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '15:00', 'end_hour': '19:00', 'number': 7}, {'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '16:00', 'end_hour': '17:00', 'number': 5}, {'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '09:00', 'end_hour': '10:00', 'number': 8}, {'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '17:00', 'end_hour': '21:00', 'number': 7}, {'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '14:00', 'end_hour': '18:00', 'number': 4}, {'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '09:00', 'end_hour': '10:00', 'number': 4}, {'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '11:00', 'end_hour': '15:00', 'number': 5}, {'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '07:00', 'end_hour': '08:00', 'number': 6}, {'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '16:00', 'end_hour': '20:00', 'number': 6}, {'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '12:00', 'end_hour': '16:00', 'number': 3}, {'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '12:00', 'end_hour': '13:00', 'number': 4}, {'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '14:00', 'end_hour': '15:00', 'number': 6}, {'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '09:00', 'end_hour': '13:00', 'number': 5}, {'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '10:00', 'end_hour': '14:00', 'number': 7}, {'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '11:00', 'end_hour': '12:00', 'number': 3}, {'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '09:00', 'end_hour': '13:00', 'number': 7}, {'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '11:00', 'end_hour': '15:00', 'number': 6}, {'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '15:00', 'end_hour': '19:00', 'number': 4}, {'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '13:00', 'end_hour': '17:00', 'number': 3}, {'profession': 'Doctor', 'day': 'Friday', 'start_hour': '15:00', 'end_hour': '19:00', 'number': 5}, {'profession': 'Doctor', 'day': 'Friday', 'start_hour': '08:00', 'end_hour': '12:00', 'number': 5}, {'profession': 'Doctor', 'day': 'Friday', 'start_hour': '13:00', 'end_hour': '14:00', 'number': 3}, {'profession': 'Doctor', 'day': 'Friday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 8}, {'profession': 'Doctor', 'day': 'Friday', 'start_hour': '14:00', 'end_hour': '15:00', 'number': 8}, {'profession': 'Doctor', 'day': 'Friday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 6}, {'profession': 'Doctor', 'day': 'Friday', 'start_hour': '11:00', 'end_hour': '12:00', 'number': 6}, {'profession': 'Doctor', 'day': 'Friday', 'start_hour': '08:00', 'end_hour': '12:00', 'number': 8}, {'profession': 'Doctor', 'day': 'Friday', 'start_hour': '09:00', 'end_hour': '13:00', 'number': 3}, {'profession': 'Doctor', 'day': 'Friday', 'start_hour': '17:00', 'end_hour': '18:00', 'number': 6}, {'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '07:00', 'end_hour': '08:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '17:00', 'end_hour': '18:00', 'number': 6}, {'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '15:00', 'end_hour': '16:00', 'number': 6}, {'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '10:00', 'end_hour': '14:00', 'number': 6}, {'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '12:00', 'end_hour': '16:00', 'number': 8}, {'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '17:00', 'end_hour': '18:00', 'number': 5}, {'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '09:00', 'end_hour': '10:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 4}, {'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 8}, {'profession': 'Teacher', 'day': 'Monday', 'start_hour': '16:00', 'end_hour': '20:00', 'number': 5}, {'profession': 'Teacher', 'day': 'Monday', 'start_hour': '14:00', 'end_hour': '18:00', 'number': 3}, {'profession': 'Teacher', 'day': 'Monday', 'start_hour': '15:00', 'end_hour': '16:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Monday', 'start_hour': '16:00', 'end_hour': '17:00', 'number': 6}, {'profession': 'Teacher', 'day': 'Monday', 'start_hour': '11:00', 'end_hour': '15:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Monday', 'start_hour': '13:00', 'end_hour': '14:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Monday', 'start_hour': '15:00', 'end_hour': '19:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Monday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Monday', 'start_hour': '10:00', 'end_hour': '14:00', 'number': 5}, {'profession': 'Teacher', 'day': 'Monday', 'start_hour': '14:00', 'end_hour': '18:00', 'number': 6}, {'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '17:00', 'end_hour': '21:00', 'number': 3}, {'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '13:00', 'end_hour': '17:00', 'number': 8}, {'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '17:00', 'end_hour': '21:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '14:00', 'end_hour': '15:00', 'number': 8}, {'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '15:00', 'end_hour': '16:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '17:00', 'end_hour': '18:00', 'number': 3}, {'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 5}, {'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 8}, {'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '16:00', 'end_hour': '17:00', 'number': 3}, {'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '12:00', 'end_hour': '16:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '17:00', 'end_hour': '18:00', 'number': 5}, {'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '17:00', 'end_hour': '18:00', 'number': 4}, {'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '15:00', 'end_hour': '19:00', 'number': 3}, {'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '13:00', 'end_hour': '14:00', 'number': 4}, {'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '14:00', 'end_hour': '18:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '13:00', 'end_hour': '17:00', 'number': 8}, {'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '16:00', 'end_hour': '17:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '17:00', 'end_hour': '21:00', 'number': 8}, {'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '14:00', 'end_hour': '15:00', 'number': 5}, {'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '12:00', 'end_hour': '16:00', 'number': 4}, {'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '14:00', 'end_hour': '18:00', 'number': 8}, {'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '14:00', 'end_hour': '15:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 4}, {'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '08:00', 'end_hour': '12:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '10:00', 'end_hour': '14:00', 'number': 4}, {'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '10:00', 'end_hour': '11:00', 'number': 8}, {'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '11:00', 'end_hour': '15:00', 'number': 8}, {'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 4}, {'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '09:00', 'end_hour': '10:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Friday', 'start_hour': '13:00', 'end_hour': '17:00', 'number': 8}, {'profession': 'Teacher', 'day': 'Friday', 'start_hour': '17:00', 'end_hour': '18:00', 'number': 5}, {'profession': 'Teacher', 'day': 'Friday', 'start_hour': '17:00', 'end_hour': '21:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Friday', 'start_hour': '16:00', 'end_hour': '20:00', 'number': 8}, {'profession': 'Teacher', 'day': 'Friday', 'start_hour': '15:00', 'end_hour': '19:00', 'number': 5}, {'profession': 'Teacher', 'day': 'Friday', 'start_hour': '10:00', 'end_hour': '11:00', 'number': 3}, {'profession': 'Teacher', 'day': 'Friday', 'start_hour': '15:00', 'end_hour': '19:00', 'number': 5}, {'profession': 'Teacher', 'day': 'Friday', 'start_hour': '15:00', 'end_hour': '16:00', 'number': 4}, {'profession': 'Teacher', 'day': 'Friday', 'start_hour': '12:00', 'end_hour': '13:00', 'number': 3}, {'profession': 'Teacher', 'day': 'Friday', 'start_hour': '14:00', 'end_hour': '18:00', 'number': 4}, {'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '11:00', 'end_hour': '12:00', 'number': 8}, {'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '12:00', 'end_hour': '13:00', 'number': 5}, {'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 6}, {'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '13:00', 'end_hour': '14:00', 'number': 8}, {'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '10:00', 'end_hour': '14:00', 'number': 7}, {'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '14:00', 'end_hour': '15:00', 'number': 4}, {'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '12:00', 'end_hour': '13:00', 'number': 8}, {'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 5}, {'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '17:00', 'end_hour': '21:00', 'number': 5}, {'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '10:00', 'end_hour': '14:00', 'number': 7}, {'profession': 'Nurse', 'day': 'Monday', 'start_hour': '16:00', 'end_hour': '20:00', 'number': 5}, {'profession': 'Nurse', 'day': 'Monday', 'start_hour': '10:00', 'end_hour': '14:00', 'number': 7}, {'profession': 'Nurse', 'day': 'Monday', 'start_hour': '11:00', 'end_hour': '15:00', 'number': 3}, {'profession': 'Nurse', 'day': 'Monday', 'start_hour': '11:00', 'end_hour': '12:00', 'number': 3}, {'profession': 'Nurse', 'day': 'Monday', 'start_hour': '14:00', 'end_hour': '15:00', 'number': 5}, {'profession': 'Nurse', 'day': 'Monday', 'start_hour': '09:00', 'end_hour': '10:00', 'number': 8}, {'profession': 'Nurse', 'day': 'Monday', 'start_hour': '09:00', 'end_hour': '13:00', 'number': 3}, {'profession': 'Nurse', 'day': 'Monday', 'start_hour': '10:00', 'end_hour': '11:00', 'number': 8}, {'profession': 'Nurse', 'day': 'Monday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 3}, {'profession': 'Nurse', 'day': 'Monday', 'start_hour': '11:00', 'end_hour': '15:00', 'number': 8}, {'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '12:00', 'end_hour': '16:00', 'number': 4}, {'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '14:00', 'end_hour': '15:00', 'number': 8}, {'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '17:00', 'end_hour': '21:00', 'number': 3}, {'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '14:00', 'end_hour': '18:00', 'number': 4}, {'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '09:00', 'end_hour': '13:00', 'number': 3}, {'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '12:00', 'end_hour': '16:00', 'number': 7}, {'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '09:00', 'end_hour': '13:00', 'number': 6}, {'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '10:00', 'end_hour': '14:00', 'number': 4}, {'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '16:00', 'end_hour': '17:00', 'number': 6}, {'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '09:00', 'end_hour': '10:00', 'number': 5}, {'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '15:00', 'end_hour': '19:00', 'number': 4}, {'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '12:00', 'end_hour': '13:00', 'number': 4}, {'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '10:00', 'end_hour': '14:00', 'number': 4}, {'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 7}, {'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '16:00', 'end_hour': '17:00', 'number': 7}, {'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '07:00', 'end_hour': '08:00', 'number': 8}, {'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '15:00', 'end_hour': '16:00', 'number': 5}, {'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '11:00', 'end_hour': '15:00', 'number': 5}, {'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '17:00', 'end_hour': '18:00', 'number': 5}, {'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '15:00', 'end_hour': '19:00', 'number': 6}, {'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '15:00', 'end_hour': '19:00', 'number': 5}, {'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '12:00', 'end_hour': '16:00', 'number': 7}, {'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '10:00', 'end_hour': '11:00', 'number': 7}, {'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '09:00', 'end_hour': '10:00', 'number': 6}, {'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 4}, {'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '14:00', 'end_hour': '15:00', 'number': 4}, {'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '16:00', 'end_hour': '17:00', 'number': 8}, {'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '10:00', 'end_hour': '14:00', 'number': 6}, {'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '16:00', 'end_hour': '20:00', 'number': 4}, {'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '09:00', 'end_hour': '10:00', 'number': 7}, {'profession': 'Nurse', 'day': 'Friday', 'start_hour': '16:00', 'end_hour': '20:00', 'number': 3}, {'profession': 'Nurse', 'day': 'Friday', 'start_hour': '11:00', 'end_hour': '15:00', 'number': 8}, {'profession': 'Nurse', 'day': 'Friday', 'start_hour': '08:00', 'end_hour': '12:00', 'number': 5}, {'profession': 'Nurse', 'day': 'Friday', 'start_hour': '11:00', 'end_hour': '12:00', 'number': 8}, {'profession': 'Nurse', 'day': 'Friday', 'start_hour': '10:00', 'end_hour': '14:00', 'number': 7}, {'profession': 'Nurse', 'day': 'Friday', 'start_hour': '12:00', 'end_hour': '16:00', 'number': 4}, {'profession': 'Nurse', 'day': 'Friday', 'start_hour': '09:00', 'end_hour': '13:00', 'number': 4}, {'profession': 'Nurse', 'day': 'Friday', 'start_hour': '10:00', 'end_hour': '11:00', 'number': 5}, {'profession': 'Nurse', 'day': 'Friday', 'start_hour': '17:00', 'end_hour': '18:00', 'number': 5}, {'profession': 'Nurse', 'day': 'Friday', 'start_hour': '13:00', 'end_hour': '14:00', 'number': 5}, {'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 8}, {'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '08:00', 'end_hour': '12:00', 'number': 4}, {'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '10:00', 'end_hour': '11:00', 'number': 6}, {'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '12:00', 'end_hour': '16:00', 'number': 5}, {'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 3}, {'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 3}, {'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 4}, {'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '12:00', 'end_hour': '16:00', 'number': 6}, {'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 4}, {'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '10:00', 'end_hour': '14:00', 'number': 6}, {'profession': 'Engineer', 'day': 'Monday', 'start_hour': '10:00', 'end_hour': '11:00', 'number': 3}, {'profession': 'Engineer', 'day': 'Monday', 'start_hour': '13:00', 'end_hour': '17:00', 'number': 8}, {'profession': 'Engineer', 'day': 'Monday', 'start_hour': '17:00', 'end_hour': '18:00', 'number': 7}, {'profession': 'Engineer', 'day': 'Monday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 5}, {'profession': 'Engineer', 'day': 'Monday', 'start_hour': '16:00', 'end_hour': '20:00', 'number': 6}, {'profession': 'Engineer', 'day': 'Monday', 'start_hour': '13:00', 'end_hour': '14:00', 'number': 5}, {'profession': 'Engineer', 'day': 'Monday', 'start_hour': '15:00', 'end_hour': '16:00', 'number': 3}, {'profession': 'Engineer', 'day': 'Monday', 'start_hour': '07:00', 'end_hour': '08:00', 'number': 3}, {'profession': 'Engineer', 'day': 'Monday', 'start_hour': '13:00', 'end_hour': '17:00', 'number': 8}, {'profession': 'Engineer', 'day': 'Monday', 'start_hour': '10:00', 'end_hour': '14:00', 'number': 7}, {'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '16:00', 'end_hour': '20:00', 'number': 5}, {'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 6}, {'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '16:00', 'end_hour': '20:00', 'number': 3}, {'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '13:00', 'end_hour': '17:00', 'number': 5}, {'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '11:00', 'end_hour': '12:00', 'number': 6}, {'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '16:00', 'end_hour': '17:00', 'number': 7}, {'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '16:00', 'end_hour': '20:00', 'number': 5}, {'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '14:00', 'end_hour': '15:00', 'number': 4}, {'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '07:00', 'end_hour': '08:00', 'number': 8}, {'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '10:00', 'end_hour': '11:00', 'number': 3}, {'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '09:00', 'end_hour': '10:00', 'number': 3}, {'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '10:00', 'end_hour': '14:00', 'number': 6}, {'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '12:00', 'end_hour': '13:00', 'number': 5}, {'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '11:00', 'end_hour': '12:00', 'number': 5}, {'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '17:00', 'end_hour': '18:00', 'number': 5}, {'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '08:00', 'end_hour': '12:00', 'number': 3}, {'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '08:00', 'end_hour': '12:00', 'number': 5}, {'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '07:00', 'end_hour': '08:00', 'number': 8}, {'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '14:00', 'end_hour': '18:00', 'number': 8}, {'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '15:00', 'end_hour': '16:00', 'number': 7}, {'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '16:00', 'end_hour': '17:00', 'number': 4}, {'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '13:00', 'end_hour': '14:00', 'number': 5}, {'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '12:00', 'end_hour': '13:00', 'number': 6}, {'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '17:00', 'end_hour': '21:00', 'number': 4}, {'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '15:00', 'end_hour': '16:00', 'number': 5}, {'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 4}, {'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '10:00', 'end_hour': '11:00', 'number': 5}, {'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 8}, {'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '13:00', 'end_hour': '17:00', 'number': 6}, {'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 7}, {'profession': 'Engineer', 'day': 'Friday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 7}, {'profession': 'Engineer', 'day': 'Friday', 'start_hour': '11:00', 'end_hour': '15:00', 'number': 3}, {'profession': 'Engineer', 'day': 'Friday', 'start_hour': '10:00', 'end_hour': '11:00', 'number': 8}, {'profession': 'Engineer', 'day': 'Friday', 'start_hour': '15:00', 'end_hour': '16:00', 'number': 4}, {'profession': 'Engineer', 'day': 'Friday', 'start_hour': '10:00', 'end_hour': '11:00', 'number': 3}, {'profession': 'Engineer', 'day': 'Friday', 'start_hour': '15:00', 'end_hour': '16:00', 'number': 5}, {'profession': 'Engineer', 'day': 'Friday', 'start_hour': '13:00', 'end_hour': '14:00', 'number': 4}, {'profession': 'Engineer', 'day': 'Friday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 4}, {'profession': 'Engineer', 'day': 'Friday', 'start_hour': '11:00', 'end_hour': '15:00', 'number': 8}, {'profession': 'Engineer', 'day': 'Friday', 'start_hour': '10:00', 'end_hour': '11:00', 'number': 3}]

idle_constrain = True
contracts_constrain = True
solution = get_assignment(shifts, workers, format_requirements, idle_constrain, contracts_constrain)




###########################
# shifts_json = json.dumps(shifts, indent=4)
# print(shifts_json)

############################3

# Convert Python workers dict to JavaScript workers_map
# js_workers_map = "let workers_map = {\n"
#
# for key, value in workers.items():
#     js_workers_map += f"  {value['id']}: {{\n"
#     js_workers_map += f"    id: {value['id']},\n"
#     js_workers_map += f"    name: \"{value['name']}\",\n"
#     js_workers_map += f"    professions: {value['professions']},\n"
#     js_workers_map += f"    days: {value['days']},\n"
#     js_workers_map += f"    shifts: [],\n"
#     js_workers_map += f"    relevant_shifts_id: [],\n"
#     js_workers_map += f"    hours_per_week: {value['hours_per_week']},\n"
#     js_workers_map += f"  }},\n"
#
# js_workers_map += "};"
#
# # Output the JavaScript code
# print(js_workers_ma
#
# ################################

# Convert to JavaScript format
# js_requirements = "let requirements = [\n"
#
# for req in requirements:
#     js_requirements += f"    {{ id: {req['id']}, profession: \"{req['profession']}\", day: \"{req['day']}\", hour: \"{req['hour']}\", number: {req['number']} }},\n"
#
# js_requirements += "];"
#
# # Print the JavaScript code
# print(js_requirements)
