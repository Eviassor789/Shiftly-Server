import pulp
import random
import copy
from itertools import product
import json
from algorithm.ILP_functions import time_to_minutes, is_overlap, find_solution, get_fitness_with_more_info, json_print
from collections import defaultdict
from datetime import datetime, timedelta
from algorithm.evolutionAlg import get_evolution_solution


def time_to_minutes(time_str):
    """Convert HH:MM time string to minutes since midnight."""
    time_obj = datetime.strptime(time_str, '%H:%M')
    return time_obj.hour * 60 + time_obj.minute

# Helper functions
def time_to_minutes_aux(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m


def is_overlap(shift1, shift2):
    start1 = time_to_minutes(shift1['start_hour'])
    end1 = time_to_minutes(shift1['end_hour'])
    start2 = time_to_minutes(shift2['start_hour'])
    end2 = time_to_minutes(shift2['end_hour'])
    return (
            ((start2 <= start1 <= end2) or
            (start2 <= end1 <= end2) or
            (start1 <= start2 <= end1) or
            (start1 <= end2 <= end1)) and
            shift1['day'] == shift2['day']
    )

def minutes_to_time(minutes):
    """Convert minutes since midnight back to HH:MM time string."""
    hours = minutes // 60
    minutes = minutes % 60
    return f"{hours:02d}:{minutes:02d}"

def re(shifts, workers, requirements):

    # Define the weights
    idle_workers_weight = 100
    contracts_weight = 100000

    cost_weight = 10
    requirements_weight = 1

    # Example data
    shifts_local = [{'id': 1, 'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '16:00', 'end_hour': '21:00', 'cost': 80},
            {'id': 2, 'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '10:00', 'end_hour': '15:00', 'cost': 80},
            {'id': 3, 'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '08:00', 'end_hour': '11:00', 'cost': 60},
            {'id': 4, 'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '12:00', 'end_hour': '15:00', 'cost': 60},
            {'id': 5, 'profession': 'Doctor', 'day': 'Monday', 'start_hour': '09:00', 'end_hour': '14:00', 'cost': 80},
            {'id': 6, 'profession': 'Doctor', 'day': 'Monday', 'start_hour': '14:00', 'end_hour': '17:00', 'cost': 60},
            {'id': 7, 'profession': 'Doctor', 'day': 'Monday', 'start_hour': '16:00', 'end_hour': '19:00', 'cost': 60},
            {'id': 8, 'profession': 'Doctor', 'day': 'Monday', 'start_hour': '10:00', 'end_hour': '13:00', 'cost': 60},
            {'id': 10, 'profession': 'Doctor', 'day': 'Tuesday', 'start_hour': '14:00', 'end_hour': '19:00', 'cost': 80},
            {'id': 11, 'profession': 'Doctor', 'day': 'Tuesday', 'start_hour': '15:00', 'end_hour': '18:00', 'cost': 60},
            {'id': 12, 'profession': 'Doctor', 'day': 'Tuesday', 'start_hour': '14:00', 'end_hour': '17:00', 'cost': 60},
            {'id': 13, 'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '14:00', 'end_hour': '19:00', 'cost': 80},
            {'id': 14, 'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '09:00', 'end_hour': '12:00', 'cost': 60},
            {'id': 15, 'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '12:00', 'end_hour': '17:00', 'cost': 80},
            {'id': 16, 'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '11:00', 'end_hour': '14:00', 'cost': 60},
            {'id': 17, 'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '14:00', 'end_hour': '17:00', 'cost': 60},
            {'id': 18, 'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '09:00', 'end_hour': '14:00', 'cost': 80},
            {'id': 19, 'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '09:00', 'end_hour': '12:00', 'cost': 60},
            {'id': 20, 'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '10:00', 'end_hour': '15:00', 'cost': 80},
            {'id': 21, 'profession': 'Doctor', 'day': 'Friday', 'start_hour': '08:00', 'end_hour': '13:00', 'cost': 80},
            {'id': 22, 'profession': 'Doctor', 'day': 'Friday', 'start_hour': '10:00', 'end_hour': '15:00', 'cost': 80},
            {'id': 23, 'profession': 'Doctor', 'day': 'Friday', 'start_hour': '14:00', 'end_hour': '17:00', 'cost': 60},
            {'id': 24, 'profession': 'Doctor', 'day': 'Friday', 'start_hour': '08:00', 'end_hour': '11:00', 'cost': 60},
            {'id': 25, 'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '10:00', 'end_hour': '13:00', 'cost': 60},
            {'id': 26, 'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '08:00', 'end_hour': '13:00', 'cost': 80},
            {'id': 27, 'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '11:00', 'end_hour': '14:00', 'cost': 60},
            {'id': 28, 'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '14:00', 'end_hour': '17:00', 'cost': 60},
            {'id': 29, 'profession': 'Teacher', 'day': 'Monday', 'start_hour': '08:00', 'end_hour': '13:00', 'cost': 80},
            {'id': 30, 'profession': 'Teacher', 'day': 'Monday', 'start_hour': '07:00', 'end_hour': '10:00', 'cost': 60},
            {'id': 32, 'profession': 'Teacher', 'day': 'Monday', 'start_hour': '16:00', 'end_hour': '21:00', 'cost': 80},
            {'id': 33, 'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '07:00', 'end_hour': '10:00', 'cost': 60},
            {'id': 34, 'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '08:00', 'end_hour': '13:00', 'cost': 80},
            {'id': 35, 'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '12:00', 'end_hour': '17:00', 'cost': 80},
            {'id': 36, 'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '10:00', 'end_hour': '13:00', 'cost': 60},
            {'id': 37, 'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '07:00', 'end_hour': '12:00', 'cost': 80},
            {'id': 38, 'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '12:00', 'end_hour': '15:00', 'cost': 60},
            {'id': 39, 'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '10:00', 'end_hour': '15:00', 'cost': 80},
            {'id': 40, 'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '12:00', 'end_hour': '17:00', 'cost': 80},
            {'id': 41, 'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '13:00', 'end_hour': '16:00', 'cost': 60},
            {'id': 42, 'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '11:00', 'end_hour': '14:00', 'cost': 60},
            {'id': 43, 'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '16:00', 'end_hour': '21:00', 'cost': 80},
            {'id': 44, 'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '09:00', 'end_hour': '12:00', 'cost': 60},
            {'id': 45, 'profession': 'Teacher', 'day': 'Friday', 'start_hour': '14:00', 'end_hour': '17:00', 'cost': 60},
            {'id': 46, 'profession': 'Teacher', 'day': 'Friday', 'start_hour': '11:00', 'end_hour': '14:00', 'cost': 60},
            {'id': 47, 'profession': 'Teacher', 'day': 'Friday', 'start_hour': '10:00', 'end_hour': '15:00', 'cost': 80},
            {'id': 48, 'profession': 'Teacher', 'day': 'Friday', 'start_hour': '10:00', 'end_hour': '15:00', 'cost': 80},
            {'id': 49, 'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '09:00', 'end_hour': '12:00', 'cost': 60},
            {'id': 50, 'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '11:00', 'end_hour': '16:00', 'cost': 80},
            {'id': 51, 'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '09:00', 'end_hour': '12:00', 'cost': 60},
            {'id': 52, 'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '08:00', 'end_hour': '13:00', 'cost': 80},
            {'id': 53, 'profession': 'Nurse', 'day': 'Monday', 'start_hour': '10:00', 'end_hour': '15:00', 'cost': 80},
            {'id': 54, 'profession': 'Nurse', 'day': 'Monday', 'start_hour': '15:00', 'end_hour': '18:00', 'cost': 60},
            {'id': 55, 'profession': 'Nurse', 'day': 'Monday', 'start_hour': '10:00', 'end_hour': '13:00', 'cost': 60},
            {'id': 56, 'profession': 'Nurse', 'day': 'Monday', 'start_hour': '08:00', 'end_hour': '13:00', 'cost': 80},
            {'id': 57, 'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '13:00', 'end_hour': '16:00', 'cost': 60},
            {'id': 58, 'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '13:00', 'end_hour': '18:00', 'cost': 80},
            {'id': 59, 'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '14:00', 'end_hour': '19:00', 'cost': 80},
            {'id': 60, 'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '09:00', 'end_hour': '12:00', 'cost': 60},
            {'id': 61, 'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '08:00', 'end_hour': '11:00', 'cost': 60},
            {'id': 62, 'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '07:00', 'end_hour': '10:00', 'cost': 60},
            {'id': 63, 'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '14:00', 'end_hour': '17:00', 'cost': 60},
            {'id': 64, 'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '16:00', 'end_hour': '19:00', 'cost': 60},
            {'id': 65, 'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '07:00', 'end_hour': '10:00', 'cost': 60},
            {'id': 66, 'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '16:00', 'end_hour': '21:00', 'cost': 80},
            {'id': 67, 'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '10:00', 'end_hour': '15:00', 'cost': 80},
            {'id': 68, 'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '07:00', 'end_hour': '12:00', 'cost': 80},
            {'id': 69, 'profession': 'Nurse', 'day': 'Friday', 'start_hour': '11:00', 'end_hour': '14:00', 'cost': 60},
            {'id': 70, 'profession': 'Nurse', 'day': 'Friday', 'start_hour': '16:00', 'end_hour': '19:00', 'cost': 60},
            {'id': 71, 'profession': 'Nurse', 'day': 'Friday', 'start_hour': '09:00', 'end_hour': '12:00', 'cost': 60},
            {'id': 72, 'profession': 'Nurse', 'day': 'Friday', 'start_hour': '10:00', 'end_hour': '13:00', 'cost': 60},
            {'id': 73, 'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '16:00', 'end_hour': '19:00', 'cost': 60},
            {'id': 74, 'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '16:00', 'end_hour': '19:00', 'cost': 60},
            {'id': 75, 'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '10:00', 'end_hour': '15:00', 'cost': 80},
            {'id': 76, 'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '11:00', 'end_hour': '16:00', 'cost': 80},
            {'id': 77, 'profession': 'Engineer', 'day': 'Monday', 'start_hour': '16:00', 'end_hour': '19:00', 'cost': 60},
            {'id': 78, 'profession': 'Engineer', 'day': 'Monday', 'start_hour': '12:00', 'end_hour': '17:00', 'cost': 80},
            {'id': 79, 'profession': 'Engineer', 'day': 'Monday', 'start_hour': '15:00', 'end_hour': '18:00', 'cost': 60},
            {'id': 80, 'profession': 'Engineer', 'day': 'Monday', 'start_hour': '07:00', 'end_hour': '10:00', 'cost': 60},
            {'id': 81, 'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '12:00', 'end_hour': '15:00', 'cost': 60},
            {'id': 82, 'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '13:00', 'end_hour': '18:00', 'cost': 80},
            {'id': 83, 'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '15:00', 'end_hour': '20:00', 'cost': 80},
            {'id': 84, 'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '11:00', 'end_hour': '16:00', 'cost': 80},
            {'id': 85, 'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '07:00', 'end_hour': '12:00',
            'cost': 80},
            {'id': 86, 'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '07:00', 'end_hour': '10:00',
            'cost': 60},
            {'id': 87, 'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '07:00', 'end_hour': '10:00',
            'cost': 60},
            {'id': 88, 'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '07:00', 'end_hour': '10:00',
            'cost': 60},
            {'id': 89, 'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '16:00', 'end_hour': '21:00', 'cost': 80},
            {'id': 90, 'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '08:00', 'end_hour': '13:00', 'cost': 80},
            {'id': 91, 'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '12:00', 'end_hour': '17:00', 'cost': 80},
            {'id': 92, 'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '10:00', 'end_hour': '13:00', 'cost': 60},
            {'id': 93, 'profession': 'Engineer', 'day': 'Friday', 'start_hour': '14:00', 'end_hour': '17:00', 'cost': 60},
            {'id': 94, 'profession': 'Engineer', 'day': 'Friday', 'start_hour': '08:00', 'end_hour': '11:00', 'cost': 60},
            {'id': 95, 'profession': 'Engineer', 'day': 'Friday', 'start_hour': '11:00', 'end_hour': '16:00', 'cost': 80},
            {'id': 96, 'profession': 'Engineer', 'day': 'Friday', 'start_hour': '11:00', 'end_hour': '16:00', 'cost': 80},

            {'id': 97, 'profession': 'Check1', 'day': 'Friday', 'start_hour': '08:00', 'end_hour': '13:00', 'cost': 80},
            {'id': 98, 'profession': 'Check2', 'day': 'Friday', 'start_hour': '12:00', 'end_hour': '19:00', 'cost': 80},
            ]

    workers_local = {0: {'id': 0, 'name': '_0', 'professions': ['Doctor', 'Engineer', 'Nurse', 'Teacher'],
                'days': ['Thursday', 'Tuesday', 'Wednesday', 'Friday', 'Monday'], 'relevant_shifts_id': [],
                'hours_per_week': 20}, 1: {'id': 1, 'name': '_1', 'professions': ['Teacher', 'Doctor', 'Nurse'],
                                            'days': ['Thursday', 'Sunday', 'Tuesday', 'Monday'], 'relevant_shifts_id': [],
                                            'hours_per_week': 11},
            2: {'id': 2, 'name': '_2', 'professions': ['Teacher', 'Engineer'],
                'days': ['Thursday', 'Friday', 'Sunday', 'Wednesday', 'Tuesday'], 'relevant_shifts_id': [],
                'hours_per_week': 20}, 3: {'id': 3, 'name': '_3', 'professions': ['Engineer', 'Nurse'],
                                            'days': ['Monday', 'Sunday', 'Friday', 'Thursday', 'Wednesday'],
                                            'relevant_shifts_id': [], 'hours_per_week': 11},
            4: {'id': 4, 'name': '_4', 'professions': ['Teacher', 'Nurse'],
                'days': ['Monday', 'Friday', 'Tuesday', 'Wednesday', 'Sunday', 'Thursday'], 'relevant_shifts_id': [],
                'hours_per_week': 16}, 5: {'id': 5, 'name': '_5', 'professions': ['Teacher', 'Nurse'],
                                            'days': ['Wednesday', 'Friday', 'Tuesday', 'Sunday', 'Thursday', 'Monday'],
                                            'relevant_shifts_id': [], 'hours_per_week': 17},
            6: {'id': 6, 'name': '_6', 'professions': ['Nurse', 'Teacher'],
                'days': ['Monday', 'Sunday', 'Tuesday', 'Wednesday'], 'relevant_shifts_id': [], 'hours_per_week': 17},
            7: {'id': 7, 'name': '_7', 'professions': ['Nurse', 'Engineer', 'Doctor', 'Teacher'],
                'days': ['Wednesday', 'Monday', 'Thursday', 'Tuesday'], 'relevant_shifts_id': [], 'hours_per_week': 5},
            8: {'id': 8, 'name': '_8', 'professions': ['Doctor', 'Teacher', 'Nurse', 'Engineer'],
                'days': ['Friday', 'Tuesday', 'Wednesday', 'Thursday'], 'relevant_shifts_id': [], 'hours_per_week': 5},
            9: {'id': 9, 'name': '_9', 'professions': ['Nurse', 'Doctor', 'Teacher'],
                'days': ['Tuesday', 'Wednesday', 'Monday', 'Friday'], 'relevant_shifts_id': [], 'hours_per_week': 14},
            10: {'id': 10, 'name': '_10', 'professions': ['Teacher', 'Engineer', 'Doctor'],
                    'days': ['Thursday', 'Friday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday'], 'relevant_shifts_id': [],
                    'hours_per_week': 17},
            11: {'id': 11, 'name': '_11', 'professions': ['Teacher', 'Nurse', 'Engineer', 'Doctor'],
                    'days': ['Thursday', 'Wednesday', 'Sunday', 'Friday'], 'relevant_shifts_id': [], 'hours_per_week': 19},
            12: {'id': 12, 'name': '_12', 'professions': ['Teacher', 'Engineer', 'Nurse'],
                    'days': ['Wednesday', 'Thursday', 'Sunday', 'Tuesday', 'Friday', 'Monday'], 'relevant_shifts_id': [],
                    'hours_per_week': 6}, 13: {'id': 13, 'name': '_13', 'professions': ['Nurse', 'Engineer', 'Doctor'],
                                            'days': ['Friday', 'Sunday', 'Tuesday', 'Monday', 'Wednesday'],
                                            'relevant_shifts_id': [], 'hours_per_week': 5},
            14: {'id': 14, 'name': '_14', 'professions': ['Teacher', 'Doctor'],
                    'days': ['Friday', 'Sunday', 'Wednesday', 'Thursday', 'Tuesday', 'Monday'], 'relevant_shifts_id': [],
                    'hours_per_week': 13},
            15: {'id': 15, 'name': '_15', 'professions': ['Engineer', 'Nurse', 'Doctor', 'Teacher'],
                    'days': ['Sunday', 'Tuesday', 'Friday', 'Wednesday', 'Thursday', 'Monday'], 'relevant_shifts_id': [],
                    'hours_per_week': 14},
            16: {'id': 16, 'name': '_16', 'professions': ['Engineer', 'Teacher', 'Nurse', 'Doctor'],
                    'days': ['Monday', 'Wednesday', 'Friday', 'Thursday', 'Tuesday'], 'relevant_shifts_id': [],
                    'hours_per_week': 8},
            17: {'id': 17, 'name': '_17', 'professions': ['Teacher', 'Doctor', 'Engineer', 'Nurse'],
                    'days': ['Sunday', 'Friday', 'Tuesday', 'Wednesday', 'Monday'], 'relevant_shifts_id': [],
                    'hours_per_week': 7}, 18: {'id': 18, 'name': '_18', 'professions': ['Teacher', 'Doctor', 'Nurse'],
                                            'days': ['Friday', 'Wednesday', 'Tuesday', 'Monday', 'Thursday'],
                                            'relevant_shifts_id': [], 'hours_per_week': 19},
            19: {'id': 19, 'name': '_19', 'professions': ['Engineer', 'Teacher', 'Doctor'],
                    'days': ['Sunday', 'Tuesday', 'Thursday', 'Wednesday', 'Friday'], 'relevant_shifts_id': [],
                    'hours_per_week': 5},
    20: {'id': 20, 'name': '_20', 'professions': ['Check1', 'Check2'],
                    'days': ['Friday'], 'relevant_shifts_id': [],
                    'hours_per_week': 4},
    21: {'id': 21, 'name': '_21', 'professions': ['Check1', 'Check2'],
                    'days': ['Friday'], 'relevant_shifts_id': [],
                    'hours_per_week': 4},
    22: {'id': 22, 'name': '_22', 'professions': ['Check1', 'Check2'],
                    'days': ['Friday'], 'relevant_shifts_id': [],
                    'hours_per_week': 4},
    23: {'id': 23, 'name': '_23', 'professions': ['Check1', 'Check2'],
                    'days': ['Friday'], 'relevant_shifts_id': [],
                    'hours_per_week': 4},
    24: {'id': 24, 'name': '_24', 'professions': ['Check1', 'Check2'],
                    'days': ['Friday'], 'relevant_shifts_id': [],
                    'hours_per_week': 4},
    25: {'id': 25, 'name': '_25', 'professions': ['Check1', 'Check2'],
                    'days': ['Friday'], 'relevant_shifts_id': [],
                    'hours_per_week': 4},
    26: {'id': 26, 'name': '_26', 'professions': ['Check1', 'Check2'],
                    'days': ['Friday'], 'relevant_shifts_id': [],
                    'hours_per_week': 4},
    27: {'id': 27, 'name': '_27', 'professions': ['Check1', 'Check2'],
                    'days': ['Friday'], 'relevant_shifts_id': [],
                    'hours_per_week': 4},
    28: {'id': 28, 'name': '_28', 'professions': ['Check1', 'Check2'],
                    'days': ['Friday'], 'relevant_shifts_id': [],
                    'hours_per_week': 4},



            }

    requirements_local = [{'id': 1, 'profession': 'Doctor', 'day': 'Sunday', 'hour': '18:00', 'number': 6},
                    {'id': 2, 'profession': 'Doctor', 'day': 'Sunday', 'hour': '13:00', 'number': 7},
                    {'id': 3, 'profession': 'Doctor', 'day': 'Sunday', 'hour': '10:00', 'number': 6},
                    {'id': 4, 'profession': 'Doctor', 'day': 'Sunday', 'hour': '15:00', 'number': 6},
                    {'id': 5, 'profession': 'Doctor', 'day': 'Sunday', 'hour': '08:00', 'number': 8},
                    {'id': 6, 'profession': 'Doctor', 'day': 'Sunday', 'hour': '15:00', 'number': 7},
                    {'id': 7, 'profession': 'Doctor', 'day': 'Sunday', 'hour': '07:00', 'number': 5},
                    {'id': 8, 'profession': 'Doctor', 'day': 'Sunday', 'hour': '08:00', 'number': 7},
                    {'id': 9, 'profession': 'Doctor', 'day': 'Sunday', 'hour': '18:00', 'number': 8},
                    {'id': 10, 'profession': 'Doctor', 'day': 'Sunday', 'hour': '14:00', 'number': 4},
                    {'id': 11, 'profession': 'Doctor', 'day': 'Monday', 'hour': '18:00', 'number': 7},
                    {'id': 12, 'profession': 'Doctor', 'day': 'Monday', 'hour': '14:00', 'number': 8},
                    {'id': 13, 'profession': 'Doctor', 'day': 'Monday', 'hour': '09:00', 'number': 5},
                    {'id': 14, 'profession': 'Doctor', 'day': 'Monday', 'hour': '14:00', 'number': 5},
                    {'id': 15, 'profession': 'Doctor', 'day': 'Monday', 'hour': '18:00', 'number': 4},
                    {'id': 16, 'profession': 'Doctor', 'day': 'Monday', 'hour': '09:00', 'number': 8},
                    {'id': 17, 'profession': 'Doctor', 'day': 'Monday', 'hour': '18:00', 'number': 6},
                    {'id': 18, 'profession': 'Doctor', 'day': 'Monday', 'hour': '18:00', 'number': 5},
                    {'id': 19, 'profession': 'Doctor', 'day': 'Monday', 'hour': '12:00', 'number': 8},
                    {'id': 20, 'profession': 'Doctor', 'day': 'Monday', 'hour': '16:00', 'number': 4},
                    {'id': 21, 'profession': 'Doctor', 'day': 'Tuesday', 'hour': '17:00', 'number': 5},
                    {'id': 22, 'profession': 'Doctor', 'day': 'Tuesday', 'hour': '17:00', 'number': 6},
                    {'id': 23, 'profession': 'Doctor', 'day': 'Tuesday', 'hour': '16:00', 'number': 4},
                    {'id': 24, 'profession': 'Doctor', 'day': 'Tuesday', 'hour': '12:00', 'number': 4},
                    {'id': 25, 'profession': 'Doctor', 'day': 'Tuesday', 'hour': '14:00', 'number': 5},
                    {'id': 26, 'profession': 'Doctor', 'day': 'Tuesday', 'hour': '18:00', 'number': 6},
                    {'id': 27, 'profession': 'Doctor', 'day': 'Tuesday', 'hour': '13:00', 'number': 7},
                    {'id': 28, 'profession': 'Doctor', 'day': 'Tuesday', 'hour': '16:00', 'number': 6},
                    {'id': 29, 'profession': 'Doctor', 'day': 'Tuesday', 'hour': '15:00', 'number': 4},
                    {'id': 30, 'profession': 'Doctor', 'day': 'Tuesday', 'hour': '16:00', 'number': 7},
                    {'id': 31, 'profession': 'Doctor', 'day': 'Wednesday', 'hour': '09:00', 'number': 4},
                    {'id': 32, 'profession': 'Doctor', 'day': 'Wednesday', 'hour': '09:00', 'number': 8},
                    {'id': 33, 'profession': 'Doctor', 'day': 'Wednesday', 'hour': '16:00', 'number': 5},
                    {'id': 34, 'profession': 'Doctor', 'day': 'Wednesday', 'hour': '17:00', 'number': 5},
                    {'id': 35, 'profession': 'Doctor', 'day': 'Wednesday', 'hour': '09:00', 'number': 6},
                    {'id': 36, 'profession': 'Doctor', 'day': 'Wednesday', 'hour': '17:00', 'number': 4},
                    {'id': 37, 'profession': 'Doctor', 'day': 'Wednesday', 'hour': '08:00', 'number': 4},
                    {'id': 38, 'profession': 'Doctor', 'day': 'Wednesday', 'hour': '18:00', 'number': 6},
                    {'id': 39, 'profession': 'Doctor', 'day': 'Wednesday', 'hour': '14:00', 'number': 7},
                    {'id': 40, 'profession': 'Doctor', 'day': 'Wednesday', 'hour': '11:00', 'number': 8},
                    {'id': 41, 'profession': 'Doctor', 'day': 'Thursday', 'hour': '13:00', 'number': 4},
                    {'id': 42, 'profession': 'Doctor', 'day': 'Thursday', 'hour': '15:00', 'number': 8},
                    {'id': 43, 'profession': 'Doctor', 'day': 'Thursday', 'hour': '11:00', 'number': 6},
                    {'id': 44, 'profession': 'Doctor', 'day': 'Thursday', 'hour': '12:00', 'number': 8},
                    {'id': 45, 'profession': 'Doctor', 'day': 'Thursday', 'hour': '18:00', 'number': 4},
                    {'id': 46, 'profession': 'Doctor', 'day': 'Thursday', 'hour': '18:00', 'number': 4},
                    {'id': 47, 'profession': 'Doctor', 'day': 'Thursday', 'hour': '13:00', 'number': 8},
                    {'id': 48, 'profession': 'Doctor', 'day': 'Thursday', 'hour': '17:00', 'number': 8},
                    {'id': 49, 'profession': 'Doctor', 'day': 'Thursday', 'hour': '18:00', 'number': 7},
                    {'id': 50, 'profession': 'Doctor', 'day': 'Thursday', 'hour': '17:00', 'number': 5},
                    {'id': 51, 'profession': 'Doctor', 'day': 'Friday', 'hour': '12:00', 'number': 8},
                    {'id': 52, 'profession': 'Doctor', 'day': 'Friday', 'hour': '12:00', 'number': 7},
                    {'id': 53, 'profession': 'Doctor', 'day': 'Friday', 'hour': '14:00', 'number': 4},
                    {'id': 54, 'profession': 'Doctor', 'day': 'Friday', 'hour': '14:00', 'number': 4},
                    {'id': 55, 'profession': 'Doctor', 'day': 'Friday', 'hour': '08:00', 'number': 8},
                    {'id': 56, 'profession': 'Doctor', 'day': 'Friday', 'hour': '14:00', 'number': 8},
                    {'id': 57, 'profession': 'Doctor', 'day': 'Friday', 'hour': '17:00', 'number': 8},
                    {'id': 58, 'profession': 'Doctor', 'day': 'Friday', 'hour': '07:00', 'number': 4},
                    {'id': 59, 'profession': 'Doctor', 'day': 'Friday', 'hour': '15:00', 'number': 7},
                    {'id': 60, 'profession': 'Doctor', 'day': 'Friday', 'hour': '11:00', 'number': 4},
                    {'id': 61, 'profession': 'Teacher', 'day': 'Sunday', 'hour': '12:00', 'number': 7},
                    {'id': 62, 'profession': 'Teacher', 'day': 'Sunday', 'hour': '16:00', 'number': 7},
                    {'id': 63, 'profession': 'Teacher', 'day': 'Sunday', 'hour': '07:00', 'number': 8},
                    {'id': 64, 'profession': 'Teacher', 'day': 'Sunday', 'hour': '14:00', 'number': 8},
                    {'id': 65, 'profession': 'Teacher', 'day': 'Sunday', 'hour': '07:00', 'number': 5},
                    {'id': 66, 'profession': 'Teacher', 'day': 'Sunday', 'hour': '16:00', 'number': 4},
                    {'id': 67, 'profession': 'Teacher', 'day': 'Sunday', 'hour': '17:00', 'number': 6},
                    {'id': 68, 'profession': 'Teacher', 'day': 'Sunday', 'hour': '09:00', 'number': 4},
                    {'id': 69, 'profession': 'Teacher', 'day': 'Sunday', 'hour': '08:00', 'number': 4},
                    {'id': 70, 'profession': 'Teacher', 'day': 'Sunday', 'hour': '09:00', 'number': 5},
                    {'id': 71, 'profession': 'Teacher', 'day': 'Monday', 'hour': '11:00', 'number': 7},
                    {'id': 72, 'profession': 'Teacher', 'day': 'Monday', 'hour': '07:00', 'number': 8},
                    {'id': 73, 'profession': 'Teacher', 'day': 'Monday', 'hour': '17:00', 'number': 7},
                    {'id': 74, 'profession': 'Teacher', 'day': 'Monday', 'hour': '12:00', 'number': 5},
                    {'id': 75, 'profession': 'Teacher', 'day': 'Monday', 'hour': '16:00', 'number': 8},
                    {'id': 76, 'profession': 'Teacher', 'day': 'Monday', 'hour': '12:00', 'number': 8},
                    {'id': 77, 'profession': 'Teacher', 'day': 'Monday', 'hour': '15:00', 'number': 4},
                    {'id': 78, 'profession': 'Teacher', 'day': 'Monday', 'hour': '08:00', 'number': 7},
                    {'id': 79, 'profession': 'Teacher', 'day': 'Monday', 'hour': '14:00', 'number': 6},
                    {'id': 80, 'profession': 'Teacher', 'day': 'Monday', 'hour': '12:00', 'number': 5},
                    {'id': 81, 'profession': 'Teacher', 'day': 'Tuesday', 'hour': '14:00', 'number': 4},
                    {'id': 82, 'profession': 'Teacher', 'day': 'Tuesday', 'hour': '12:00', 'number': 5},
                    {'id': 83, 'profession': 'Teacher', 'day': 'Tuesday', 'hour': '11:00', 'number': 4},
                    {'id': 84, 'profession': 'Teacher', 'day': 'Tuesday', 'hour': '12:00', 'number': 6},
                    {'id': 85, 'profession': 'Teacher', 'day': 'Tuesday', 'hour': '18:00', 'number': 8},
                    {'id': 86, 'profession': 'Teacher', 'day': 'Tuesday', 'hour': '18:00', 'number': 6},
                    {'id': 87, 'profession': 'Teacher', 'day': 'Tuesday', 'hour': '15:00', 'number': 4},
                    {'id': 88, 'profession': 'Teacher', 'day': 'Tuesday', 'hour': '10:00', 'number': 6},
                    {'id': 89, 'profession': 'Teacher', 'day': 'Tuesday', 'hour': '17:00', 'number': 6},
                    {'id': 90, 'profession': 'Teacher', 'day': 'Tuesday', 'hour': '14:00', 'number': 7},
                    {'id': 91, 'profession': 'Teacher', 'day': 'Wednesday', 'hour': '09:00', 'number': 7},
                    {'id': 92, 'profession': 'Teacher', 'day': 'Wednesday', 'hour': '16:00', 'number': 5},
                    {'id': 93, 'profession': 'Teacher', 'day': 'Wednesday', 'hour': '10:00', 'number': 5},
                    {'id': 94, 'profession': 'Teacher', 'day': 'Wednesday', 'hour': '11:00', 'number': 5},
                    {'id': 95, 'profession': 'Teacher', 'day': 'Wednesday', 'hour': '16:00', 'number': 7},
                    {'id': 96, 'profession': 'Teacher', 'day': 'Wednesday', 'hour': '18:00', 'number': 5},
                    {'id': 97, 'profession': 'Teacher', 'day': 'Wednesday', 'hour': '16:00', 'number': 6},
                    {'id': 98, 'profession': 'Teacher', 'day': 'Wednesday', 'hour': '12:00', 'number': 5},
                    {'id': 99, 'profession': 'Teacher', 'day': 'Wednesday', 'hour': '16:00', 'number': 5},
                    {'id': 100, 'profession': 'Teacher', 'day': 'Wednesday', 'hour': '13:00', 'number': 7},
                    {'id': 101, 'profession': 'Teacher', 'day': 'Thursday', 'hour': '09:00', 'number': 7},
                    {'id': 102, 'profession': 'Teacher', 'day': 'Thursday', 'hour': '16:00', 'number': 7},
                    {'id': 103, 'profession': 'Teacher', 'day': 'Thursday', 'hour': '17:00', 'number': 8},
                    {'id': 104, 'profession': 'Teacher', 'day': 'Thursday', 'hour': '07:00', 'number': 8},
                    {'id': 105, 'profession': 'Teacher', 'day': 'Thursday', 'hour': '07:00', 'number': 6},
                    {'id': 106, 'profession': 'Teacher', 'day': 'Thursday', 'hour': '09:00', 'number': 5},
                    {'id': 107, 'profession': 'Teacher', 'day': 'Thursday', 'hour': '14:00', 'number': 7},
                    {'id': 108, 'profession': 'Teacher', 'day': 'Thursday', 'hour': '12:00', 'number': 7},
                    {'id': 109, 'profession': 'Teacher', 'day': 'Thursday', 'hour': '08:00', 'number': 7},
                    {'id': 110, 'profession': 'Teacher', 'day': 'Thursday', 'hour': '18:00', 'number': 5},
                    {'id': 111, 'profession': 'Teacher', 'day': 'Friday', 'hour': '18:00', 'number': 6},
                    {'id': 112, 'profession': 'Teacher', 'day': 'Friday', 'hour': '13:00', 'number': 4},
                    {'id': 113, 'profession': 'Teacher', 'day': 'Friday', 'hour': '13:00', 'number': 8},
                    {'id': 114, 'profession': 'Teacher', 'day': 'Friday', 'hour': '07:00', 'number': 5},
                    {'id': 115, 'profession': 'Teacher', 'day': 'Friday', 'hour': '11:00', 'number': 5},
                    {'id': 116, 'profession': 'Teacher', 'day': 'Friday', 'hour': '13:00', 'number': 8},
                    {'id': 117, 'profession': 'Teacher', 'day': 'Friday', 'hour': '15:00', 'number': 6},
                    {'id': 118, 'profession': 'Teacher', 'day': 'Friday', 'hour': '14:00', 'number': 7},
                    {'id': 119, 'profession': 'Teacher', 'day': 'Friday', 'hour': '17:00', 'number': 8},
                    {'id': 120, 'profession': 'Teacher', 'day': 'Friday', 'hour': '08:00', 'number': 7},
                    {'id': 121, 'profession': 'Nurse', 'day': 'Sunday', 'hour': '17:00', 'number': 6},
                    {'id': 122, 'profession': 'Nurse', 'day': 'Sunday', 'hour': '09:00', 'number': 8},
                    {'id': 123, 'profession': 'Nurse', 'day': 'Sunday', 'hour': '07:00', 'number': 5},
                    {'id': 124, 'profession': 'Nurse', 'day': 'Sunday', 'hour': '13:00', 'number': 6},
                    {'id': 125, 'profession': 'Nurse', 'day': 'Sunday', 'hour': '18:00', 'number': 6},
                    {'id': 126, 'profession': 'Nurse', 'day': 'Sunday', 'hour': '09:00', 'number': 6},
                    {'id': 127, 'profession': 'Nurse', 'day': 'Sunday', 'hour': '18:00', 'number': 7},
                    {'id': 128, 'profession': 'Nurse', 'day': 'Sunday', 'hour': '12:00', 'number': 5},
                    {'id': 129, 'profession': 'Nurse', 'day': 'Sunday', 'hour': '10:00', 'number': 6},
                    {'id': 130, 'profession': 'Nurse', 'day': 'Sunday', 'hour': '10:00', 'number': 4},
                    {'id': 131, 'profession': 'Nurse', 'day': 'Monday', 'hour': '13:00', 'number': 5},
                    {'id': 132, 'profession': 'Nurse', 'day': 'Monday', 'hour': '12:00', 'number': 5},
                    {'id': 133, 'profession': 'Nurse', 'day': 'Monday', 'hour': '12:00', 'number': 7},
                    {'id': 134, 'profession': 'Nurse', 'day': 'Monday', 'hour': '12:00', 'number': 5},
                    {'id': 135, 'profession': 'Nurse', 'day': 'Monday', 'hour': '11:00', 'number': 8},
                    {'id': 136, 'profession': 'Nurse', 'day': 'Monday', 'hour': '07:00', 'number': 5},
                    {'id': 137, 'profession': 'Nurse', 'day': 'Monday', 'hour': '10:00', 'number': 7},
                    {'id': 138, 'profession': 'Nurse', 'day': 'Monday', 'hour': '18:00', 'number': 4},
                    {'id': 139, 'profession': 'Nurse', 'day': 'Monday', 'hour': '15:00', 'number': 4},
                    {'id': 140, 'profession': 'Nurse', 'day': 'Monday', 'hour': '15:00', 'number': 8},
                    {'id': 141, 'profession': 'Nurse', 'day': 'Tuesday', 'hour': '15:00', 'number': 4},
                    {'id': 142, 'profession': 'Nurse', 'day': 'Tuesday', 'hour': '18:00', 'number': 6},
                    {'id': 143, 'profession': 'Nurse', 'day': 'Tuesday', 'hour': '16:00', 'number': 5},
                    {'id': 144, 'profession': 'Nurse', 'day': 'Tuesday', 'hour': '07:00', 'number': 5},
                    {'id': 145, 'profession': 'Nurse', 'day': 'Tuesday', 'hour': '14:00', 'number': 7},
                    {'id': 146, 'profession': 'Nurse', 'day': 'Tuesday', 'hour': '15:00', 'number': 4},
                    {'id': 147, 'profession': 'Nurse', 'day': 'Tuesday', 'hour': '08:00', 'number': 4},
                    {'id': 148, 'profession': 'Nurse', 'day': 'Tuesday', 'hour': '16:00', 'number': 6},
                    {'id': 149, 'profession': 'Nurse', 'day': 'Tuesday', 'hour': '15:00', 'number': 7},
                    {'id': 150, 'profession': 'Nurse', 'day': 'Tuesday', 'hour': '11:00', 'number': 6},
                    {'id': 151, 'profession': 'Nurse', 'day': 'Wednesday', 'hour': '16:00', 'number': 5},
                    {'id': 152, 'profession': 'Nurse', 'day': 'Wednesday', 'hour': '16:00', 'number': 6},
                    {'id': 153, 'profession': 'Nurse', 'day': 'Wednesday', 'hour': '17:00', 'number': 7},
                    {'id': 154, 'profession': 'Nurse', 'day': 'Wednesday', 'hour': '18:00', 'number': 5},
                    {'id': 155, 'profession': 'Nurse', 'day': 'Wednesday', 'hour': '13:00', 'number': 5},
                    {'id': 156, 'profession': 'Nurse', 'day': 'Wednesday', 'hour': '18:00', 'number': 6},
                    {'id': 157, 'profession': 'Nurse', 'day': 'Wednesday', 'hour': '10:00', 'number': 6},
                    {'id': 158, 'profession': 'Nurse', 'day': 'Wednesday', 'hour': '14:00', 'number': 8},
                    {'id': 159, 'profession': 'Nurse', 'day': 'Wednesday', 'hour': '09:00', 'number': 4},
                    {'id': 160, 'profession': 'Nurse', 'day': 'Wednesday', 'hour': '15:00', 'number': 7},
                    {'id': 161, 'profession': 'Nurse', 'day': 'Thursday', 'hour': '17:00', 'number': 7},
                    {'id': 162, 'profession': 'Nurse', 'day': 'Thursday', 'hour': '12:00', 'number': 5},
                    {'id': 163, 'profession': 'Nurse', 'day': 'Thursday', 'hour': '14:00', 'number': 6},
                    {'id': 164, 'profession': 'Nurse', 'day': 'Thursday', 'hour': '17:00', 'number': 6},
                    {'id': 165, 'profession': 'Nurse', 'day': 'Thursday', 'hour': '09:00', 'number': 4},
                    {'id': 166, 'profession': 'Nurse', 'day': 'Thursday', 'hour': '11:00', 'number': 7},
                    {'id': 167, 'profession': 'Nurse', 'day': 'Thursday', 'hour': '17:00', 'number': 7},
                    {'id': 168, 'profession': 'Nurse', 'day': 'Thursday', 'hour': '16:00', 'number': 7},
                    {'id': 169, 'profession': 'Nurse', 'day': 'Thursday', 'hour': '10:00', 'number': 8},
                    {'id': 170, 'profession': 'Nurse', 'day': 'Thursday', 'hour': '08:00', 'number': 8},
                    {'id': 171, 'profession': 'Nurse', 'day': 'Friday', 'hour': '10:00', 'number': 7},
                    {'id': 172, 'profession': 'Nurse', 'day': 'Friday', 'hour': '15:00', 'number': 7},
                    {'id': 173, 'profession': 'Nurse', 'day': 'Friday', 'hour': '12:00', 'number': 6},
                    {'id': 174, 'profession': 'Nurse', 'day': 'Friday', 'hour': '13:00', 'number': 7},
                    {'id': 175, 'profession': 'Nurse', 'day': 'Friday', 'hour': '11:00', 'number': 7},
                    {'id': 176, 'profession': 'Nurse', 'day': 'Friday', 'hour': '12:00', 'number': 4},
                    {'id': 177, 'profession': 'Nurse', 'day': 'Friday', 'hour': '09:00', 'number': 7},
                    {'id': 178, 'profession': 'Nurse', 'day': 'Friday', 'hour': '14:00', 'number': 8},
                    {'id': 179, 'profession': 'Nurse', 'day': 'Friday', 'hour': '10:00', 'number': 5},
                    {'id': 180, 'profession': 'Nurse', 'day': 'Friday', 'hour': '09:00', 'number': 8},
                    {'id': 181, 'profession': 'Engineer', 'day': 'Sunday', 'hour': '10:00', 'number': 8},
                    {'id': 182, 'profession': 'Engineer', 'day': 'Sunday', 'hour': '08:00', 'number': 4},
                    {'id': 183, 'profession': 'Engineer', 'day': 'Sunday', 'hour': '14:00', 'number': 7},
                    {'id': 184, 'profession': 'Engineer', 'day': 'Sunday', 'hour': '08:00', 'number': 4},
                    {'id': 185, 'profession': 'Engineer', 'day': 'Sunday', 'hour': '11:00', 'number': 5},
                    {'id': 186, 'profession': 'Engineer', 'day': 'Sunday', 'hour': '10:00', 'number': 4},
                    {'id': 187, 'profession': 'Engineer', 'day': 'Sunday', 'hour': '11:00', 'number': 7},
                    {'id': 188, 'profession': 'Engineer', 'day': 'Sunday', 'hour': '09:00', 'number': 4},
                    {'id': 189, 'profession': 'Engineer', 'day': 'Sunday', 'hour': '09:00', 'number': 6},
                    {'id': 190, 'profession': 'Engineer', 'day': 'Sunday', 'hour': '07:00', 'number': 8},
                    {'id': 191, 'profession': 'Engineer', 'day': 'Monday', 'hour': '18:00', 'number': 7},
                    {'id': 192, 'profession': 'Engineer', 'day': 'Monday', 'hour': '09:00', 'number': 8},
                    {'id': 193, 'profession': 'Engineer', 'day': 'Monday', 'hour': '12:00', 'number': 8},
                    {'id': 194, 'profession': 'Engineer', 'day': 'Monday', 'hour': '08:00', 'number': 5},
                    {'id': 195, 'profession': 'Engineer', 'day': 'Monday', 'hour': '13:00', 'number': 7},
                    {'id': 196, 'profession': 'Engineer', 'day': 'Monday', 'hour': '18:00', 'number': 7},
                    {'id': 197, 'profession': 'Engineer', 'day': 'Monday', 'hour': '17:00', 'number': 6},
                    {'id': 198, 'profession': 'Engineer', 'day': 'Monday', 'hour': '09:00', 'number': 4},
                    {'id': 199, 'profession': 'Engineer', 'day': 'Monday', 'hour': '13:00', 'number': 6},
                    {'id': 200, 'profession': 'Engineer', 'day': 'Monday', 'hour': '07:00', 'number': 7},
                    {'id': 201, 'profession': 'Engineer', 'day': 'Tuesday', 'hour': '14:00', 'number': 6},
                    {'id': 202, 'profession': 'Engineer', 'day': 'Tuesday', 'hour': '11:00', 'number': 6},
                    {'id': 203, 'profession': 'Engineer', 'day': 'Tuesday', 'hour': '14:00', 'number': 8},
                    {'id': 204, 'profession': 'Engineer', 'day': 'Tuesday', 'hour': '12:00', 'number': 8},
                    {'id': 205, 'profession': 'Engineer', 'day': 'Tuesday', 'hour': '11:00', 'number': 5},
                    {'id': 206, 'profession': 'Engineer', 'day': 'Tuesday', 'hour': '14:00', 'number': 4},
                    {'id': 207, 'profession': 'Engineer', 'day': 'Tuesday', 'hour': '15:00', 'number': 6},
                    {'id': 208, 'profession': 'Engineer', 'day': 'Tuesday', 'hour': '10:00', 'number': 8},
                    {'id': 209, 'profession': 'Engineer', 'day': 'Tuesday', 'hour': '12:00', 'number': 7},
                    {'id': 210, 'profession': 'Engineer', 'day': 'Tuesday', 'hour': '12:00', 'number': 4},
                    {'id': 211, 'profession': 'Engineer', 'day': 'Wednesday', 'hour': '16:00', 'number': 4},
                    {'id': 212, 'profession': 'Engineer', 'day': 'Wednesday', 'hour': '10:00', 'number': 5},
                    {'id': 213, 'profession': 'Engineer', 'day': 'Wednesday', 'hour': '07:00', 'number': 6},
                    {'id': 214, 'profession': 'Engineer', 'day': 'Wednesday', 'hour': '14:00', 'number': 8},
                    {'id': 215, 'profession': 'Engineer', 'day': 'Wednesday', 'hour': '17:00', 'number': 7},
                    {'id': 216, 'profession': 'Engineer', 'day': 'Wednesday', 'hour': '12:00', 'number': 6},
                    {'id': 217, 'profession': 'Engineer', 'day': 'Wednesday', 'hour': '17:00', 'number': 5},
                    {'id': 218, 'profession': 'Engineer', 'day': 'Wednesday', 'hour': '08:00', 'number': 6},
                    {'id': 219, 'profession': 'Engineer', 'day': 'Wednesday', 'hour': '12:00', 'number': 8},
                    {'id': 220, 'profession': 'Engineer', 'day': 'Wednesday', 'hour': '14:00', 'number': 4},
                    {'id': 221, 'profession': 'Engineer', 'day': 'Thursday', 'hour': '09:00', 'number': 4},
                    {'id': 222, 'profession': 'Engineer', 'day': 'Thursday', 'hour': '07:00', 'number': 4},
                    {'id': 223, 'profession': 'Engineer', 'day': 'Thursday', 'hour': '11:00', 'number': 5},
                    {'id': 224, 'profession': 'Engineer', 'day': 'Thursday', 'hour': '16:00', 'number': 4},
                    {'id': 225, 'profession': 'Engineer', 'day': 'Thursday', 'hour': '16:00', 'number': 8},
                    {'id': 226, 'profession': 'Engineer', 'day': 'Thursday', 'hour': '13:00', 'number': 5},
                    {'id': 227, 'profession': 'Engineer', 'day': 'Thursday', 'hour': '13:00', 'number': 6},
                    {'id': 228, 'profession': 'Engineer', 'day': 'Thursday', 'hour': '09:00', 'number': 5},
                    {'id': 229, 'profession': 'Engineer', 'day': 'Thursday', 'hour': '16:00', 'number': 7},
                    {'id': 230, 'profession': 'Engineer', 'day': 'Thursday', 'hour': '18:00', 'number': 8},
                    {'id': 231, 'profession': 'Engineer', 'day': 'Friday', 'hour': '07:00', 'number': 4},
                    {'id': 232, 'profession': 'Engineer', 'day': 'Friday', 'hour': '13:00', 'number': 4},
                    {'id': 233, 'profession': 'Engineer', 'day': 'Friday', 'hour': '13:00', 'number': 5},
                    {'id': 234, 'profession': 'Engineer', 'day': 'Friday', 'hour': '15:00', 'number': 4},
                    {'id': 235, 'profession': 'Engineer', 'day': 'Friday', 'hour': '12:00', 'number': 8},
                    {'id': 236, 'profession': 'Engineer', 'day': 'Friday', 'hour': '12:00', 'number': 7},
                    {'id': 237, 'profession': 'Engineer', 'day': 'Friday', 'hour': '10:00', 'number': 8},
                    {'id': 238, 'profession': 'Engineer', 'day': 'Friday', 'hour': '18:00', 'number': 6},
                    {'id': 239, 'profession': 'Engineer', 'day': 'Friday', 'hour': '08:00', 'number': 5},
                    {'id': 240, 'profession': 'Engineer', 'day': 'Friday', 'hour': '15:00', 'number': 8},

                    {'id': 242, 'profession': 'Check2', 'day': 'Friday', 'hour': '12:00', 'number': 8},
                    {'id': 243, 'profession': 'Check2', 'day': 'Friday', 'hour': '13:00', 'number': 8},
                    {'id': 244, 'profession': 'Check2', 'day': 'Friday', 'hour': '14:00', 'number': 8},
                    {'id': 245, 'profession': 'Check2', 'day': 'Friday', 'hour': '15:00', 'number': 8},
                    {'id': 246, 'profession': 'Check2', 'day': 'Friday', 'hour': '16:00', 'number': 8},
                    {'id': 247, 'profession': 'Check2', 'day': 'Friday', 'hour': '17:00', 'number': 8},
                    {'id': 248, 'profession': 'Check2', 'day': 'Friday', 'hour': '18:00', 'number': 8},

                    {'id': 249, 'profession': 'Check1', 'day': 'Friday', 'hour': '08:00', 'number': 8},
                    {'id': 250, 'profession': 'Check1', 'day': 'Friday', 'hour': '09:00', 'number': 8},
                    {'id': 251, 'profession': 'Check1', 'day': 'Friday', 'hour': '10:00', 'number': 8},
                    {'id': 252, 'profession': 'Check1', 'day': 'Friday', 'hour': '11:00', 'number': 8},
                    {'id': 253, 'profession': 'Check1', 'day': 'Friday', 'hour': '12:00', 'number': 8},

                    ]






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
                            time_to_minutes_aux(s['start_hour']) <= time_to_minutes_aux(req['hour']) < time_to_minutes_aux(
            s['end_hour'])
                            for req in requirements)

        if not has_requirements:
            # Add a constraint to ensure the shift is left empty
            for w in workers:
                model += assignments[workers[w]['id'], s['id']] == 0

    # Add binary variables for each requirement
    req_satisfied = {req['id']: pulp.LpVariable(f"req_satisfied_{req['id']}", cat='Binary') for req in requirements}

    # Add constraints to link binary variables with actual satisfaction of requirements
    for req in requirements:
        model += pulp.lpSum(assignments[(workers[w]['id'], s['id'])]
                            for w in workers for s in shifts
                            if req['profession'] == s['profession'] and
                            req['day'] == s['day'] and
                            time_to_minutes_aux(s['start_hour']) <= time_to_minutes_aux(req['hour']) < time_to_minutes_aux(s['end_hour'])
                            ) >= req['number'] * req_satisfied[req['id']]

    # Calculate total cost
    total_cost = pulp.lpSum(assignments[(workers[w]['id'], s['id'])] * s['cost'] for w in workers for s in shifts)

    # Calculate the number of satisfied contracts
    satisfied_contracts = pulp.lpSum(pulp.lpSum(
        assignments[(workers[w]['id'], s['id'])] * (time_to_minutes_aux(s['end_hour']) - time_to_minutes_aux(s['start_hour'])) / 60
        for s in shifts) >= workers[w]['hours_per_week'] for w in workers)

    shift_to_largest_req = {
        s['id']: max(
            req['number'] for req in requirements if req['profession'] == s['profession'] and req['day'] == s['day'] and
            time_to_minutes_aux(s['start_hour']) <= time_to_minutes_aux(req['hour']) < time_to_minutes_aux(s['end_hour']))
        for s in shifts
        if any(req['profession'] == s['profession'] and req['day'] == s['day'] and
            time_to_minutes_aux(s['start_hour']) <= time_to_minutes_aux(req['hour']) < time_to_minutes_aux(s['end_hour'])
            for req in requirements)
    }

    # Calculate the number of idle workers based on the largest requirement for each shift
    idle_workers_vars = pulp.LpVariable.dicts("idle_workers", ((s['id']) for s in shifts), lowBound=0, cat='Integer')

    for s in shifts:
        if any(req['profession'] == s['profession'] and req['day'] == s['day'] and
            time_to_minutes_aux(s['start_hour']) <= time_to_minutes_aux(req['hour']) < time_to_minutes_aux(s['end_hour'])
            for req in requirements):
            workers_num = pulp.lpSum(assignments[(workers[w]['id'], s['id'])] for w in workers)
            model += idle_workers_vars[(s['id'])] >= pulp.lpSum(assignments[(workers[w]['id'], s['id'])] for w in workers) - \
                    shift_to_largest_req[s['id']]
            model += idle_workers_vars[(s['id'])] >= 0


    idle_workers = pulp.lpSum(idle_workers_vars[(s['id'])] for s in shifts)

    # Objective: Weighted sum of the objectives
    model += (
                    contracts_weight * satisfied_contracts
                    + requirements_weight * pulp.lpSum(assignments[(workers[w]['id'], s['id'])] for w in workers for s in shifts)
                    - cost_weight * total_cost
                    - idle_workers_weight * idle_workers
            ), "Optimize Objectives"

    # Solve the model
    model.solve()

    # Output the results
    print("Status:", pulp.LpStatus[model.status])
    for w in workers:
        for s in shifts:
            if pulp.value(assignments[(workers[w]['id'], s['id'])]) == 1:
                print(f"Worker {workers[w]['id']} is assigned to Shift {s['id']}")

    # Extract the solution
    solution = [(w_id, s_id) for (w_id, s_id), var in assignments.items() if pulp.value(var) == 1]
    solution = sorted(solution, key=lambda x: x[1])
    return solution



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
    # return re(shifts, workers, requirements)

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


# # Example data
# shifts = [{'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '12:00', 'end_hour': '17:00', 'cost': 80}, {'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '15:00', 'end_hour': '20:00', 'cost': 80}, {'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '14:00', 'end_hour': '17:00', 'cost': 60}, {'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '15:00', 'end_hour': '18:00', 'cost': 60}, {'profession': 'Doctor', 'day': 'Monday', 'start_hour': '08:00', 'end_hour': '13:00', 'cost': 80}, {'profession': 'Doctor', 'day': 'Monday', 'start_hour': '10:00', 'end_hour': '13:00', 'cost': 60}, {'profession': 'Doctor', 'day': 'Monday', 'start_hour': '10:00', 'end_hour': '15:00', 'cost': 80}, {'profession': 'Doctor', 'day': 'Monday', 'start_hour': '11:00', 'end_hour': '14:00', 'cost': 60}, {'profession': 'Doctor', 'day': 'Tuesday', 'start_hour': '07:00', 'end_hour': '12:00', 'cost': 80}, {'profession': 'Doctor', 'day': 'Tuesday', 'start_hour': '12:00', 'end_hour': '17:00', 'cost': 80}, {'profession': 'Doctor', 'day': 'Tuesday', 'start_hour': '10:00', 'end_hour': '15:00', 'cost': 80}, {'profession': 'Doctor', 'day': 'Tuesday', 'start_hour': '08:00', 'end_hour': '11:00', 'cost': 60}, {'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '07:00', 'end_hour': '10:00', 'cost': 60}, {'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '07:00', 'end_hour': '10:00', 'cost': 60}, {'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '09:00', 'end_hour': '12:00', 'cost': 60}, {'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '13:00', 'end_hour': '18:00', 'cost': 80}, {'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '13:00', 'end_hour': '18:00', 'cost': 80}, {'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '08:00', 'end_hour': '11:00', 'cost': 60}, {'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '10:00', 'end_hour': '15:00', 'cost': 80}, {'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '14:00', 'end_hour': '17:00', 'cost': 60}, {'profession': 'Doctor', 'day': 'Friday', 'start_hour': '15:00', 'end_hour': '20:00', 'cost': 80}, {'profession': 'Doctor', 'day': 'Friday', 'start_hour': '08:00', 'end_hour': '13:00', 'cost': 80}, {'profession': 'Doctor', 'day': 'Friday', 'start_hour': '08:00', 'end_hour': '11:00', 'cost': 60}, {'profession': 'Doctor', 'day': 'Friday', 'start_hour': '14:00', 'end_hour': '17:00', 'cost': 60}, {'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '08:00', 'end_hour': '13:00', 'cost': 80}, {'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '07:00', 'end_hour': '10:00', 'cost': 60}, {'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '09:00', 'end_hour': '14:00', 'cost': 80}, {'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '07:00', 'end_hour': '12:00', 'cost': 80}, {'profession': 'Teacher', 'day': 'Monday', 'start_hour': '11:00', 'end_hour': '16:00', 'cost': 80}, {'profession': 'Teacher', 'day': 'Monday', 'start_hour': '12:00', 'end_hour': '17:00', 'cost': 80}, {'profession': 'Teacher', 'day': 'Monday', 'start_hour': '09:00', 'end_hour': '14:00', 'cost': 80}, {'profession': 'Teacher', 'day': 'Monday', 'start_hour': '15:00', 'end_hour': '18:00', 'cost': 60}, {'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '15:00', 'end_hour': '18:00', 'cost': 60}, {'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '09:00', 'end_hour': '12:00', 'cost': 60}, {'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '12:00', 'end_hour': '17:00', 'cost': 80}, {'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '08:00', 'end_hour': '11:00', 'cost': 60}, {'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '13:00', 'end_hour': '18:00', 'cost': 80}, {'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '15:00', 'end_hour': '18:00', 'cost': 60}, {'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '12:00', 'end_hour': '15:00', 'cost': 60}, {'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '11:00', 'end_hour': '16:00', 'cost': 80}, {'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '07:00', 'end_hour': '10:00', 'cost': 60}, {'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '08:00', 'end_hour': '13:00', 'cost': 80}, {'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '12:00', 'end_hour': '15:00', 'cost': 60}, {'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '12:00', 'end_hour': '15:00', 'cost': 60}, {'profession': 'Teacher', 'day': 'Friday', 'start_hour': '12:00', 'end_hour': '15:00', 'cost': 60}, {'profession': 'Teacher', 'day': 'Friday', 'start_hour': '09:00', 'end_hour': '12:00', 'cost': 60}, {'profession': 'Teacher', 'day': 'Friday', 'start_hour': '12:00', 'end_hour': '17:00', 'cost': 80}, {'profession': 'Teacher', 'day': 'Friday', 'start_hour': '14:00', 'end_hour': '19:00', 'cost': 80}, {'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '08:00', 'end_hour': '11:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '12:00', 'end_hour': '17:00', 'cost': 80}, {'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '10:00', 'end_hour': '13:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '08:00', 'end_hour': '11:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Monday', 'start_hour': '15:00', 'end_hour': '18:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Monday', 'start_hour': '08:00', 'end_hour': '11:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Monday', 'start_hour': '15:00', 'end_hour': '18:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Monday', 'start_hour': '15:00', 'end_hour': '20:00', 'cost': 80}, {'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '07:00', 'end_hour': '12:00', 'cost': 80}, {'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '11:00', 'end_hour': '14:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '07:00', 'end_hour': '10:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '12:00', 'end_hour': '15:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '14:00', 'end_hour': '17:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '14:00', 'end_hour': '17:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '08:00', 'end_hour': '11:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '08:00', 'end_hour': '13:00', 'cost': 80}, {'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '15:00', 'end_hour': '18:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '08:00', 'end_hour': '13:00', 'cost': 80}, {'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '15:00', 'end_hour': '18:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '09:00', 'end_hour': '12:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Friday', 'start_hour': '07:00', 'end_hour': '10:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Friday', 'start_hour': '10:00', 'end_hour': '13:00', 'cost': 60}, {'profession': 'Nurse', 'day': 'Friday', 'start_hour': '15:00', 'end_hour': '20:00', 'cost': 80}, {'profession': 'Nurse', 'day': 'Friday', 'start_hour': '14:00', 'end_hour': '17:00', 'cost': 60}, {'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '07:00', 'end_hour': '12:00', 'cost': 80}, {'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '11:00', 'end_hour': '14:00', 'cost': 60}, {'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '11:00', 'end_hour': '14:00', 'cost': 60}, {'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '13:00', 'end_hour': '16:00', 'cost': 60}, {'profession': 'Engineer', 'day': 'Monday', 'start_hour': '13:00', 'end_hour': '16:00', 'cost': 60}, {'profession': 'Engineer', 'day': 'Monday', 'start_hour': '12:00', 'end_hour': '15:00', 'cost': 60}, {'profession': 'Engineer', 'day': 'Monday', 'start_hour': '11:00', 'end_hour': '16:00', 'cost': 80}, {'profession': 'Engineer', 'day': 'Monday', 'start_hour': '10:00', 'end_hour': '15:00', 'cost': 80}, {'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '14:00', 'end_hour': '17:00', 'cost': 60}, {'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '10:00', 'end_hour': '15:00', 'cost': 80}, {'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '09:00', 'end_hour': '14:00', 'cost': 80}, {'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '09:00', 'end_hour': '12:00', 'cost': 60}, {'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '15:00', 'end_hour': '20:00', 'cost': 80}, {'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '11:00', 'end_hour': '16:00', 'cost': 80}, {'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '09:00', 'end_hour': '14:00', 'cost': 80}, {'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '14:00', 'end_hour': '19:00', 'cost': 80}, {'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '14:00', 'end_hour': '19:00', 'cost': 80}, {'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '12:00', 'end_hour': '15:00', 'cost': 60}, {'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '09:00', 'end_hour': '14:00', 'cost': 80}, {'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '14:00', 'end_hour': '17:00', 'cost': 60}, {'profession': 'Engineer', 'day': 'Friday', 'start_hour': '15:00', 'end_hour': '20:00', 'cost': 80}, {'profession': 'Engineer', 'day': 'Friday', 'start_hour': '10:00', 'end_hour': '15:00', 'cost': 80}, {'profession': 'Engineer', 'day': 'Friday', 'start_hour': '07:00', 'end_hour': '10:00', 'cost': 60}, {'profession': 'Engineer', 'day': 'Friday', 'start_hour': '15:00', 'end_hour': '18:00', 'cost': 60}]

# workers = {0: {'id': 0, 'name': '_0', 'professions': ['Nurse', 'Engineer'], 'days': ['Friday', 'Sunday', 'Wednesday', 'Monday', 'Thursday', 'Tuesday'], 'relevant_shifts_id': [], 'hours_per_week': 7}, 1: {'id': 1, 'name': '_1', 'professions': ['Doctor', 'Teacher', 'Engineer', 'Nurse'], 'days': ['Friday', 'Thursday', 'Monday', 'Wednesday', 'Tuesday'], 'relevant_shifts_id': [], 'hours_per_week': 5}, 2: {'id': 2, 'name': '_2', 'professions': ['Engineer', 'Teacher', 'Doctor', 'Nurse'], 'days': ['Thursday', 'Sunday', 'Friday', 'Wednesday', 'Tuesday'], 'relevant_shifts_id': [], 'hours_per_week': 8}, 3: {'id': 3, 'name': '_3', 'professions': ['Teacher', 'Doctor', 'Engineer'], 'days': ['Monday', 'Friday', 'Tuesday', 'Thursday', 'Sunday', 'Wednesday'], 'relevant_shifts_id': [], 'hours_per_week': 11}, 4: {'id': 4, 'name': '_4', 'professions': ['Engineer', 'Teacher', 'Nurse', 'Doctor'], 'days': ['Sunday', 'Monday', 'Thursday', 'Wednesday', 'Friday', 'Tuesday'], 'relevant_shifts_id': [], 'hours_per_week': 8}, 5: {'id': 5, 'name': '_5', 'professions': ['Nurse', 'Engineer'], 'days': ['Sunday', 'Tuesday', 'Monday', 'Wednesday', 'Thursday', 'Friday'], 'relevant_shifts_id': [], 'hours_per_week': 7}, 6: {'id': 6, 'name': '_6', 'professions': ['Nurse', 'Doctor', 'Teacher'], 'days': ['Tuesday', 'Sunday', 'Thursday', 'Friday', 'Monday', 'Wednesday'], 'relevant_shifts_id': [], 'hours_per_week': 11}, 7: {'id': 7, 'name': '_7', 'professions': ['Engineer', 'Nurse'], 'days': ['Sunday', 'Wednesday', 'Friday', 'Thursday', 'Monday'], 'relevant_shifts_id': [], 'hours_per_week': 11}, 8: {'id': 8, 'name': '_8', 'professions': ['Teacher', 'Engineer', 'Doctor'], 'days': ['Tuesday', 'Monday', 'Sunday', 'Thursday', 'Friday'], 'relevant_shifts_id': [], 'hours_per_week': 7}, 9: {'id': 9, 'name': '_9', 'professions': ['Nurse', 'Doctor'], 'days': ['Tuesday', 'Wednesday', 'Monday', 'Thursday', 'Friday'], 'relevant_shifts_id': [], 'hours_per_week': 18}, 10: {'id': 10, 'name': '_10', 'professions': ['Engineer', 'Nurse', 'Doctor'], 'days': ['Sunday', 'Friday', 'Monday', 'Wednesday'], 'relevant_shifts_id': [], 'hours_per_week': 8}, 11: {'id': 11, 'name': '_11', 'professions': ['Doctor', 'Teacher', 'Engineer'], 'days': ['Wednesday', 'Sunday', 'Friday', 'Thursday'], 'relevant_shifts_id': [], 'hours_per_week': 6}, 12: {'id': 12, 'name': '_12', 'professions': ['Engineer', 'Doctor', 'Nurse', 'Teacher'], 'days': ['Wednesday', 'Sunday', 'Monday', 'Friday'], 'relevant_shifts_id': [], 'hours_per_week': 6}, 13: {'id': 13, 'name': '_13', 'professions': ['Doctor', 'Engineer', 'Nurse', 'Teacher'], 'days': ['Friday', 'Thursday', 'Tuesday', 'Sunday', 'Wednesday', 'Monday'], 'relevant_shifts_id': [], 'hours_per_week': 10}, 14: {'id': 14, 'name': '_14', 'professions': ['Engineer', 'Nurse'], 'days': ['Thursday', 'Monday', 'Tuesday', 'Wednesday', 'Sunday', 'Friday'], 'relevant_shifts_id': [], 'hours_per_week': 6}, 15: {'id': 15, 'name': '_15', 'professions': ['Doctor', 'Teacher', 'Nurse'], 'days': ['Tuesday', 'Monday', 'Thursday', 'Friday'], 'relevant_shifts_id': [], 'hours_per_week': 13}, 16: {'id': 16, 'name': '_16', 'professions': ['Teacher', 'Nurse', 'Doctor', 'Engineer'], 'days': ['Tuesday', 'Thursday', 'Friday', 'Monday'], 'relevant_shifts_id': [], 'hours_per_week': 13}, 17: {'id': 17, 'name': '_17', 'professions': ['Engineer', 'Doctor', 'Teacher', 'Nurse'], 'days': ['Thursday', 'Tuesday', 'Sunday', 'Wednesday'], 'relevant_shifts_id': [], 'hours_per_week': 14}, 18: {'id': 18, 'name': '_18', 'professions': ['Nurse', 'Teacher', 'Doctor'], 'days': ['Wednesday', 'Sunday', 'Thursday', 'Tuesday', 'Friday'], 'relevant_shifts_id': [], 'hours_per_week': 5}, 19: {'id': 19, 'name': '_19', 'professions': ['Engineer', 'Teacher', 'Doctor'], 'days': ['Wednesday', 'Tuesday', 'Monday', 'Thursday', 'Sunday', 'Friday'], 'relevant_shifts_id': [], 'hours_per_week': 14}}

# format_requirements = [{'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '13:00', 'end_hour': '14:00', 'number': 6}, {'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '15:00', 'end_hour': '19:00', 'number': 8}, {'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '13:00', 'end_hour': '14:00', 'number': 8}, {'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '12:00', 'end_hour': '16:00', 'number': 8}, {'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '17:00', 'end_hour': '18:00', 'number': 3}, {'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '10:00', 'end_hour': '14:00', 'number': 8}, {'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 7}, {'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 3}, {'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '17:00', 'end_hour': '18:00', 'number': 6}, {'profession': 'Doctor', 'day': 'Sunday', 'start_hour': '12:00', 'end_hour': '16:00', 'number': 6}, {'profession': 'Doctor', 'day': 'Monday', 'start_hour': '10:00', 'end_hour': '11:00', 'number': 5}, {'profession': 'Doctor', 'day': 'Monday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 8}, {'profession': 'Doctor', 'day': 'Monday', 'start_hour': '15:00', 'end_hour': '19:00', 'number': 7}, {'profession': 'Doctor', 'day': 'Monday', 'start_hour': '07:00', 'end_hour': '08:00', 'number': 8}, {'profession': 'Doctor', 'day': 'Monday', 'start_hour': '07:00', 'end_hour': '08:00', 'number': 7}, {'profession': 'Doctor', 'day': 'Monday', 'start_hour': '14:00', 'end_hour': '15:00', 'number': 6}, {'profession': 'Doctor', 'day': 'Monday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 3}, {'profession': 'Doctor', 'day': 'Monday', 'start_hour': '16:00', 'end_hour': '17:00', 'number': 4}, {'profession': 'Doctor', 'day': 'Monday', 'start_hour': '12:00', 'end_hour': '16:00', 'number': 8}, {'profession': 'Doctor', 'day': 'Monday', 'start_hour': '10:00', 'end_hour': '11:00', 'number': 3}, {'profession': 'Doctor', 'day': 'Tuesday', 'start_hour': '13:00', 'end_hour': '14:00', 'number': 8}, {'profession': 'Doctor', 'day': 'Tuesday', 'start_hour': '07:00', 'end_hour': '08:00', 'number': 6}, {'profession': 'Doctor', 'day': 'Tuesday', 'start_hour': '10:00', 'end_hour': '11:00', 'number': 7}, {'profession': 'Doctor', 'day': 'Tuesday', 'start_hour': '17:00', 'end_hour': '21:00', 'number': 7}, {'profession': 'Doctor', 'day': 'Tuesday', 'start_hour': '16:00', 'end_hour': '20:00', 'number': 6}, {'profession': 'Doctor', 'day': 'Tuesday', 'start_hour': '11:00', 'end_hour': '15:00', 'number': 4}, {'profession': 'Doctor', 'day': 'Tuesday', 'start_hour': '15:00', 'end_hour': '16:00', 'number': 3}, {'profession': 'Doctor', 'day': 'Tuesday', 'start_hour': '09:00', 'end_hour': '10:00', 'number': 4}, {'profession': 'Doctor', 'day': 'Tuesday', 'start_hour': '16:00', 'end_hour': '17:00', 'number': 8}, {'profession': 'Doctor', 'day': 'Tuesday', 'start_hour': '12:00', 'end_hour': '13:00', 'number': 3}, {'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '12:00', 'end_hour': '13:00', 'number': 4}, {'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '15:00', 'end_hour': '19:00', 'number': 7}, {'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '16:00', 'end_hour': '17:00', 'number': 5}, {'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '09:00', 'end_hour': '10:00', 'number': 8}, {'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '17:00', 'end_hour': '21:00', 'number': 7}, {'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '14:00', 'end_hour': '18:00', 'number': 4}, {'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '09:00', 'end_hour': '10:00', 'number': 4}, {'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '11:00', 'end_hour': '15:00', 'number': 5}, {'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '07:00', 'end_hour': '08:00', 'number': 6}, {'profession': 'Doctor', 'day': 'Wednesday', 'start_hour': '16:00', 'end_hour': '20:00', 'number': 6}, {'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '12:00', 'end_hour': '16:00', 'number': 3}, {'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '12:00', 'end_hour': '13:00', 'number': 4}, {'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '14:00', 'end_hour': '15:00', 'number': 6}, {'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '09:00', 'end_hour': '13:00', 'number': 5}, {'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '10:00', 'end_hour': '14:00', 'number': 7}, {'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '11:00', 'end_hour': '12:00', 'number': 3}, {'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '09:00', 'end_hour': '13:00', 'number': 7}, {'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '11:00', 'end_hour': '15:00', 'number': 6}, {'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '15:00', 'end_hour': '19:00', 'number': 4}, {'profession': 'Doctor', 'day': 'Thursday', 'start_hour': '13:00', 'end_hour': '17:00', 'number': 3}, {'profession': 'Doctor', 'day': 'Friday', 'start_hour': '15:00', 'end_hour': '19:00', 'number': 5}, {'profession': 'Doctor', 'day': 'Friday', 'start_hour': '08:00', 'end_hour': '12:00', 'number': 5}, {'profession': 'Doctor', 'day': 'Friday', 'start_hour': '13:00', 'end_hour': '14:00', 'number': 3}, {'profession': 'Doctor', 'day': 'Friday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 8}, {'profession': 'Doctor', 'day': 'Friday', 'start_hour': '14:00', 'end_hour': '15:00', 'number': 8}, {'profession': 'Doctor', 'day': 'Friday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 6}, {'profession': 'Doctor', 'day': 'Friday', 'start_hour': '11:00', 'end_hour': '12:00', 'number': 6}, {'profession': 'Doctor', 'day': 'Friday', 'start_hour': '08:00', 'end_hour': '12:00', 'number': 8}, {'profession': 'Doctor', 'day': 'Friday', 'start_hour': '09:00', 'end_hour': '13:00', 'number': 3}, {'profession': 'Doctor', 'day': 'Friday', 'start_hour': '17:00', 'end_hour': '18:00', 'number': 6}, {'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '07:00', 'end_hour': '08:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '17:00', 'end_hour': '18:00', 'number': 6}, {'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '15:00', 'end_hour': '16:00', 'number': 6}, {'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '10:00', 'end_hour': '14:00', 'number': 6}, {'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '12:00', 'end_hour': '16:00', 'number': 8}, {'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '17:00', 'end_hour': '18:00', 'number': 5}, {'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '09:00', 'end_hour': '10:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 4}, {'profession': 'Teacher', 'day': 'Sunday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 8}, {'profession': 'Teacher', 'day': 'Monday', 'start_hour': '16:00', 'end_hour': '20:00', 'number': 5}, {'profession': 'Teacher', 'day': 'Monday', 'start_hour': '14:00', 'end_hour': '18:00', 'number': 3}, {'profession': 'Teacher', 'day': 'Monday', 'start_hour': '15:00', 'end_hour': '16:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Monday', 'start_hour': '16:00', 'end_hour': '17:00', 'number': 6}, {'profession': 'Teacher', 'day': 'Monday', 'start_hour': '11:00', 'end_hour': '15:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Monday', 'start_hour': '13:00', 'end_hour': '14:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Monday', 'start_hour': '15:00', 'end_hour': '19:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Monday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Monday', 'start_hour': '10:00', 'end_hour': '14:00', 'number': 5}, {'profession': 'Teacher', 'day': 'Monday', 'start_hour': '14:00', 'end_hour': '18:00', 'number': 6}, {'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '17:00', 'end_hour': '21:00', 'number': 3}, {'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '13:00', 'end_hour': '17:00', 'number': 8}, {'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '17:00', 'end_hour': '21:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '14:00', 'end_hour': '15:00', 'number': 8}, {'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '15:00', 'end_hour': '16:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '17:00', 'end_hour': '18:00', 'number': 3}, {'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 5}, {'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 8}, {'profession': 'Teacher', 'day': 'Tuesday', 'start_hour': '16:00', 'end_hour': '17:00', 'number': 3}, {'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '12:00', 'end_hour': '16:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '17:00', 'end_hour': '18:00', 'number': 5}, {'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '17:00', 'end_hour': '18:00', 'number': 4}, {'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '15:00', 'end_hour': '19:00', 'number': 3}, {'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '13:00', 'end_hour': '14:00', 'number': 4}, {'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '14:00', 'end_hour': '18:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '13:00', 'end_hour': '17:00', 'number': 8}, {'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '16:00', 'end_hour': '17:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '17:00', 'end_hour': '21:00', 'number': 8}, {'profession': 'Teacher', 'day': 'Wednesday', 'start_hour': '14:00', 'end_hour': '15:00', 'number': 5}, {'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '12:00', 'end_hour': '16:00', 'number': 4}, {'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '14:00', 'end_hour': '18:00', 'number': 8}, {'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '14:00', 'end_hour': '15:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 4}, {'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '08:00', 'end_hour': '12:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '10:00', 'end_hour': '14:00', 'number': 4}, {'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '10:00', 'end_hour': '11:00', 'number': 8}, {'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '11:00', 'end_hour': '15:00', 'number': 8}, {'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 4}, {'profession': 'Teacher', 'day': 'Thursday', 'start_hour': '09:00', 'end_hour': '10:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Friday', 'start_hour': '13:00', 'end_hour': '17:00', 'number': 8}, {'profession': 'Teacher', 'day': 'Friday', 'start_hour': '17:00', 'end_hour': '18:00', 'number': 5}, {'profession': 'Teacher', 'day': 'Friday', 'start_hour': '17:00', 'end_hour': '21:00', 'number': 7}, {'profession': 'Teacher', 'day': 'Friday', 'start_hour': '16:00', 'end_hour': '20:00', 'number': 8}, {'profession': 'Teacher', 'day': 'Friday', 'start_hour': '15:00', 'end_hour': '19:00', 'number': 5}, {'profession': 'Teacher', 'day': 'Friday', 'start_hour': '10:00', 'end_hour': '11:00', 'number': 3}, {'profession': 'Teacher', 'day': 'Friday', 'start_hour': '15:00', 'end_hour': '19:00', 'number': 5}, {'profession': 'Teacher', 'day': 'Friday', 'start_hour': '15:00', 'end_hour': '16:00', 'number': 4}, {'profession': 'Teacher', 'day': 'Friday', 'start_hour': '12:00', 'end_hour': '13:00', 'number': 3}, {'profession': 'Teacher', 'day': 'Friday', 'start_hour': '14:00', 'end_hour': '18:00', 'number': 4}, {'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '11:00', 'end_hour': '12:00', 'number': 8}, {'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '12:00', 'end_hour': '13:00', 'number': 5}, {'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 6}, {'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '13:00', 'end_hour': '14:00', 'number': 8}, {'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '10:00', 'end_hour': '14:00', 'number': 7}, {'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '14:00', 'end_hour': '15:00', 'number': 4}, {'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '12:00', 'end_hour': '13:00', 'number': 8}, {'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 5}, {'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '17:00', 'end_hour': '21:00', 'number': 5}, {'profession': 'Nurse', 'day': 'Sunday', 'start_hour': '10:00', 'end_hour': '14:00', 'number': 7}, {'profession': 'Nurse', 'day': 'Monday', 'start_hour': '16:00', 'end_hour': '20:00', 'number': 5}, {'profession': 'Nurse', 'day': 'Monday', 'start_hour': '10:00', 'end_hour': '14:00', 'number': 7}, {'profession': 'Nurse', 'day': 'Monday', 'start_hour': '11:00', 'end_hour': '15:00', 'number': 3}, {'profession': 'Nurse', 'day': 'Monday', 'start_hour': '11:00', 'end_hour': '12:00', 'number': 3}, {'profession': 'Nurse', 'day': 'Monday', 'start_hour': '14:00', 'end_hour': '15:00', 'number': 5}, {'profession': 'Nurse', 'day': 'Monday', 'start_hour': '09:00', 'end_hour': '10:00', 'number': 8}, {'profession': 'Nurse', 'day': 'Monday', 'start_hour': '09:00', 'end_hour': '13:00', 'number': 3}, {'profession': 'Nurse', 'day': 'Monday', 'start_hour': '10:00', 'end_hour': '11:00', 'number': 8}, {'profession': 'Nurse', 'day': 'Monday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 3}, {'profession': 'Nurse', 'day': 'Monday', 'start_hour': '11:00', 'end_hour': '15:00', 'number': 8}, {'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '12:00', 'end_hour': '16:00', 'number': 4}, {'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '14:00', 'end_hour': '15:00', 'number': 8}, {'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '17:00', 'end_hour': '21:00', 'number': 3}, {'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '14:00', 'end_hour': '18:00', 'number': 4}, {'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '09:00', 'end_hour': '13:00', 'number': 3}, {'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '12:00', 'end_hour': '16:00', 'number': 7}, {'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '09:00', 'end_hour': '13:00', 'number': 6}, {'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '10:00', 'end_hour': '14:00', 'number': 4}, {'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '16:00', 'end_hour': '17:00', 'number': 6}, {'profession': 'Nurse', 'day': 'Tuesday', 'start_hour': '09:00', 'end_hour': '10:00', 'number': 5}, {'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '15:00', 'end_hour': '19:00', 'number': 4}, {'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '12:00', 'end_hour': '13:00', 'number': 4}, {'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '10:00', 'end_hour': '14:00', 'number': 4}, {'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 7}, {'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '16:00', 'end_hour': '17:00', 'number': 7}, {'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '07:00', 'end_hour': '08:00', 'number': 8}, {'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '15:00', 'end_hour': '16:00', 'number': 5}, {'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '11:00', 'end_hour': '15:00', 'number': 5}, {'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '17:00', 'end_hour': '18:00', 'number': 5}, {'profession': 'Nurse', 'day': 'Wednesday', 'start_hour': '15:00', 'end_hour': '19:00', 'number': 6}, {'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '15:00', 'end_hour': '19:00', 'number': 5}, {'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '12:00', 'end_hour': '16:00', 'number': 7}, {'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '10:00', 'end_hour': '11:00', 'number': 7}, {'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '09:00', 'end_hour': '10:00', 'number': 6}, {'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 4}, {'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '14:00', 'end_hour': '15:00', 'number': 4}, {'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '16:00', 'end_hour': '17:00', 'number': 8}, {'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '10:00', 'end_hour': '14:00', 'number': 6}, {'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '16:00', 'end_hour': '20:00', 'number': 4}, {'profession': 'Nurse', 'day': 'Thursday', 'start_hour': '09:00', 'end_hour': '10:00', 'number': 7}, {'profession': 'Nurse', 'day': 'Friday', 'start_hour': '16:00', 'end_hour': '20:00', 'number': 3}, {'profession': 'Nurse', 'day': 'Friday', 'start_hour': '11:00', 'end_hour': '15:00', 'number': 8}, {'profession': 'Nurse', 'day': 'Friday', 'start_hour': '08:00', 'end_hour': '12:00', 'number': 5}, {'profession': 'Nurse', 'day': 'Friday', 'start_hour': '11:00', 'end_hour': '12:00', 'number': 8}, {'profession': 'Nurse', 'day': 'Friday', 'start_hour': '10:00', 'end_hour': '14:00', 'number': 7}, {'profession': 'Nurse', 'day': 'Friday', 'start_hour': '12:00', 'end_hour': '16:00', 'number': 4}, {'profession': 'Nurse', 'day': 'Friday', 'start_hour': '09:00', 'end_hour': '13:00', 'number': 4}, {'profession': 'Nurse', 'day': 'Friday', 'start_hour': '10:00', 'end_hour': '11:00', 'number': 5}, {'profession': 'Nurse', 'day': 'Friday', 'start_hour': '17:00', 'end_hour': '18:00', 'number': 5}, {'profession': 'Nurse', 'day': 'Friday', 'start_hour': '13:00', 'end_hour': '14:00', 'number': 5}, {'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 8}, {'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '08:00', 'end_hour': '12:00', 'number': 4}, {'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '10:00', 'end_hour': '11:00', 'number': 6}, {'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '12:00', 'end_hour': '16:00', 'number': 5}, {'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 3}, {'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 3}, {'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 4}, {'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '12:00', 'end_hour': '16:00', 'number': 6}, {'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 4}, {'profession': 'Engineer', 'day': 'Sunday', 'start_hour': '10:00', 'end_hour': '14:00', 'number': 6}, {'profession': 'Engineer', 'day': 'Monday', 'start_hour': '10:00', 'end_hour': '11:00', 'number': 3}, {'profession': 'Engineer', 'day': 'Monday', 'start_hour': '13:00', 'end_hour': '17:00', 'number': 8}, {'profession': 'Engineer', 'day': 'Monday', 'start_hour': '17:00', 'end_hour': '18:00', 'number': 7}, {'profession': 'Engineer', 'day': 'Monday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 5}, {'profession': 'Engineer', 'day': 'Monday', 'start_hour': '16:00', 'end_hour': '20:00', 'number': 6}, {'profession': 'Engineer', 'day': 'Monday', 'start_hour': '13:00', 'end_hour': '14:00', 'number': 5}, {'profession': 'Engineer', 'day': 'Monday', 'start_hour': '15:00', 'end_hour': '16:00', 'number': 3}, {'profession': 'Engineer', 'day': 'Monday', 'start_hour': '07:00', 'end_hour': '08:00', 'number': 3}, {'profession': 'Engineer', 'day': 'Monday', 'start_hour': '13:00', 'end_hour': '17:00', 'number': 8}, {'profession': 'Engineer', 'day': 'Monday', 'start_hour': '10:00', 'end_hour': '14:00', 'number': 7}, {'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '16:00', 'end_hour': '20:00', 'number': 5}, {'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 6}, {'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '16:00', 'end_hour': '20:00', 'number': 3}, {'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '13:00', 'end_hour': '17:00', 'number': 5}, {'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '11:00', 'end_hour': '12:00', 'number': 6}, {'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '16:00', 'end_hour': '17:00', 'number': 7}, {'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '16:00', 'end_hour': '20:00', 'number': 5}, {'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '14:00', 'end_hour': '15:00', 'number': 4}, {'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '07:00', 'end_hour': '08:00', 'number': 8}, {'profession': 'Engineer', 'day': 'Tuesday', 'start_hour': '10:00', 'end_hour': '11:00', 'number': 3}, {'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '09:00', 'end_hour': '10:00', 'number': 3}, {'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '10:00', 'end_hour': '14:00', 'number': 6}, {'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '12:00', 'end_hour': '13:00', 'number': 5}, {'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '11:00', 'end_hour': '12:00', 'number': 5}, {'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '17:00', 'end_hour': '18:00', 'number': 5}, {'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '08:00', 'end_hour': '12:00', 'number': 3}, {'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '08:00', 'end_hour': '12:00', 'number': 5}, {'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '07:00', 'end_hour': '08:00', 'number': 8}, {'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '14:00', 'end_hour': '18:00', 'number': 8}, {'profession': 'Engineer', 'day': 'Wednesday', 'start_hour': '15:00', 'end_hour': '16:00', 'number': 7}, {'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '16:00', 'end_hour': '17:00', 'number': 4}, {'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '13:00', 'end_hour': '14:00', 'number': 5}, {'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '12:00', 'end_hour': '13:00', 'number': 6}, {'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '17:00', 'end_hour': '21:00', 'number': 4}, {'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '15:00', 'end_hour': '16:00', 'number': 5}, {'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 4}, {'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '10:00', 'end_hour': '11:00', 'number': 5}, {'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 8}, {'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '13:00', 'end_hour': '17:00', 'number': 6}, {'profession': 'Engineer', 'day': 'Thursday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 7}, {'profession': 'Engineer', 'day': 'Friday', 'start_hour': '07:00', 'end_hour': '11:00', 'number': 7}, {'profession': 'Engineer', 'day': 'Friday', 'start_hour': '11:00', 'end_hour': '15:00', 'number': 3}, {'profession': 'Engineer', 'day': 'Friday', 'start_hour': '10:00', 'end_hour': '11:00', 'number': 8}, {'profession': 'Engineer', 'day': 'Friday', 'start_hour': '15:00', 'end_hour': '16:00', 'number': 4}, {'profession': 'Engineer', 'day': 'Friday', 'start_hour': '10:00', 'end_hour': '11:00', 'number': 3}, {'profession': 'Engineer', 'day': 'Friday', 'start_hour': '15:00', 'end_hour': '16:00', 'number': 5}, {'profession': 'Engineer', 'day': 'Friday', 'start_hour': '13:00', 'end_hour': '14:00', 'number': 4}, {'profession': 'Engineer', 'day': 'Friday', 'start_hour': '08:00', 'end_hour': '09:00', 'number': 4}, {'profession': 'Engineer', 'day': 'Friday', 'start_hour': '11:00', 'end_hour': '15:00', 'number': 8}, {'profession': 'Engineer', 'day': 'Friday', 'start_hour': '10:00', 'end_hour': '11:00', 'number': 3}]

# idle_constrain = True
# contracts_constrain = True
# solution = get_assignment(shifts, workers, format_requirements, idle_constrain, contracts_constrain)
# assignment = json_print(solution)



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
