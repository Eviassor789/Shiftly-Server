import random
import pandas as pd

# Constants
days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
professions = ["Doctor", "Teacher", "Nurse", "Engineer"]
hours_range = list(range(7, 21))  # 07:00 to 20:00
num_workers = 20
day_to_number = {day: i + 1 for i, day in enumerate(days)}

def format_hour(hour):
    """Helper function to format hours into HH:MM."""
    return f"{hour:02d}:00"

# Generate shifts_list
shifts_list = []
shift_id = 1
for profession in professions:
    for day in days:
        for i in range(4):  # 4 different shifts per day per profession
            start_hour = random.choice(hours_range[:-5])
            end_hour = start_hour + random.choice([3, 5])
            cost = ((end_hour - start_hour) * 10) + 30
            shift = {
                "profession": profession,
                "day": day,
                "start_hour": format_hour(start_hour),
                "end_hour": format_hour(end_hour),
                "cost": cost,
            }
            shifts_list.append(shift)
            shift_id += 1

# Generate requirements_list
requirements_list = []
requirement_id = 1
for profession in professions:
    for day in days:
        for i in range(2):  # At least 2 requirements per day per profession
            start_hour = random.choice(hours_range[:-3])
            end_hour = start_hour + random.choice([1, 4])
            number = random.randint(3, 8)  # At least 3 workers needed
            requirement = {
                "profession": profession,
                "day": day,
                "start_hour": format_hour(start_hour),
                "end_hour": format_hour(end_hour),
                "number": number,
            }
            requirements_list.append(requirement)
            requirement_id += 1

# Generate workers_map
workers_map = {}
for i in range(num_workers):
    worker_id = i
    name = f"Worker_{chr(ord('A') + worker_id)}"
    professions_sample = random.sample(professions, k=random.randint(2, 4))
    days_sample = random.sample(days, k=random.randint(4, 6))
    hours_per_week = random.randint(5, 20)

    workers_map[worker_id] = {
        "id": worker_id,
        "name": name,
        "professions": professions_sample,
        "days": days_sample,
        "relevant_shifts_id": [],
        "hours_per_week": hours_per_week,
    }

# Convert to DataFrames for Excel export
shifts_df = pd.DataFrame([
    [shift['profession'], day_to_number[shift['day']], shift['start_hour'], shift['end_hour'], shift['cost']]
    for shift in shifts_list
], columns=['Profession', 'Day', 'Start Hour', 'End Hour', 'Cost'])

requirements_df = pd.DataFrame([
    [day_to_number[requirement['day']], requirement['profession'], requirement['start_hour'], requirement['end_hour'], requirement['number']]
    for requirement in requirements_list
], columns=['Day', 'Profession', 'Start Hour', 'End Hour', 'Number'])

# Ensure the DataFrame has enough columns for all possible professions
workers_df = pd.DataFrame([
    [
        worker['id'],
        worker['name'],
        worker['professions'][0] if len(worker['professions']) > 0 else '',
        worker['professions'][1] if len(worker['professions']) > 1 else '',
        worker['professions'][2] if len(worker['professions']) > 2 else '',
        worker['hours_per_week'],
        ','.join(str(day_to_number[day]) for day in worker['days'])
    ]
    for worker in workers_map.values()
], columns=['ID', 'Name', 'Profession1', 'Profession2', 'Profession3', 'Hours per Week', 'Days'])

# Save to Excel files in the current working directory
shifts_df.to_excel('shifts.xlsx', index=False, header=False)
requirements_df.to_excel('requirements.xlsx', index=False, header=False)
workers_df.to_excel('workers.xlsx', index=False, header=False)


shifts_df.head(), requirements_df.head(), workers_df.head()


# # Output
# print("Shifts List:", shifts_list)
# print("Requirements List:", requirements_list)
# print("Workers Map:", workers_map)

