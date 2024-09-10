import random
from flask import Flask, jsonify, request, redirect, url_for, session
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from flask_cors import CORS, cross_origin
from models import User, Table, Shift, Worker, Requirement
from algorithm.ILP import get_assignment, json_print, process_requirements, time_to_minutes, minutes_to_time
from base import Session, create_tables
from datetime import datetime, timedelta

from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests
import os

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
app.secret_key = 'your-secret-key'
jwt = JWTManager(app)

# Extend the JWT access token expiration time (e.g., 8 hours)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=8)

# Optionally, set refresh token expiration time (e.g., 30 days)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize the database (create tables if they don't exist)
create_tables()

# Create a test user if it doesn't already exist
def create_test_user(username, password, tablesArr, picture="", settings=[False, True], color="#178f36"):
    session = Session()
    if not session.query(User).filter_by(username=username).first():
        test_user = User(
            username=username,
            tablesArr=tablesArr,
            picture=picture,
            settings=settings,
            color=color
        )
        test_user.set_password(password)
        session.add(test_user)
        session.commit()
        print(f"Test user created: username='{username}', password='{password}'")
    else:
        print("Test user already exists")
    session.close()  # Close session

create_test_user("gon", "ggg", [111, 112, 113])

def fetch_user_from_db(username):
    session = Session()
    user = session.query(User).filter_by(username=username).first()
    session.close()  # Close session
    return user

@app.route('/get_user_data', methods=['POST'])
@jwt_required()
def get_user_data():
    data = request.json
    username = data.get('username')
    
    session = Session()
    user = session.query(User).filter_by(username=username).first()
    session.close()
    
    if user:
        return jsonify(tablesArr=user.tablesArr)
    return jsonify(msg="User not found"), 404


# Logic to return the correct day based on the input
def get_day(shift_day):
    
    daysOfWeek = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    
    # Check if shift_day is a digit (e.g., "1", "2", etc.)
    if shift_day.isdigit():
        # Convert to integer and map to the corresponding day of the week
        return daysOfWeek[int(shift_day) - 1]
    else:
        # If shift_day is not a digit, assume it's already a day name and return it as-is
        return shift_day


@app.route('/user_tables', methods=['GET'])
@jwt_required()
@cross_origin()
def get_user_tables():
    current_user = get_jwt_identity()
    session = Session()
    
    try:
        user = session.query(User).filter_by(username=current_user).first()
        if not user:
            return jsonify(msg="User not found"), 404
        
        table_ids = user.tablesArr
        tables = session.query(Table).filter(Table.id.in_(table_ids)).all()
        
        tables_list = [{
            "id": table.id,
            "name": table.name,
            "date": table.date,
            "starred": table.starred,
            "professions": table.professions,
            "shifts": [{
                "id": shift.id,
                "profession": shift.profession,
                "day": get_day(shift.day),
                "start_hour": shift.start_hour,
                "end_hour": shift.end_hour,
                "cost": shift.cost,
                "workers": [{
                    "id": worker.id,
                    "name": worker.name,
                    "professions": worker.professions,
                    "days": worker.days,
                    "hours_per_week": worker.hours_per_week,
                    "table_id": worker.table_id
                } for worker in shift.workers],  # Include worker details
                "color": shift.color
            } for shift in table.shifts],
            "assignment": table.assignment
        } for table in tables]
        
        return jsonify(tables_list)
    
    except Exception as e:
        return jsonify(msg=str(e)), 500
    
    finally:
        session.close()


@app.route('/table/<int:table_id>', methods=['GET'])
@jwt_required()
@cross_origin()
def get_table_data(table_id):
    current_user = get_jwt_identity()
    session = Session()
    
    try:
        user = session.query(User).filter_by(username=current_user).first()
        if not user:
            return jsonify(msg="User not found"), 404
        
        # Query the table from the database based on the table_id
        table = session.query(Table).filter_by(id=table_id).first()

        if not table:
            return jsonify({'error': 'Table not found'}), 404
        
        all_workers = session.query(Worker).filter_by(table_id=table_id).all()
                
        table_data = {
            "id": table.id,
            "name": table.name,
            "date": table.date,
            "starred": table.starred,
            "professions": table.professions,
            "shifts": [{
                "id": shift.id,
                "profession": shift.profession,
                "day": get_day(shift.day),
                "start_hour": shift.start_hour,
                "end_hour": shift.end_hour,
                "cost": shift.cost,
                "workers": [{
                    "id": worker.id,
                    "name": worker.name,
                    "professions": worker.professions,
                    "days": worker.days,
                    "hours_per_week": worker.hours_per_week,
                    "table_id": worker.table_id
                } for worker in shift.workers],  # Include worker details
                "color": shift.color
            } for shift in table.shifts],
            "assignment": table.assignment,
            "all_workers": [{
                    "id": worker.id,
                    "name": worker.name,
                    "professions": worker.professions,
                    "days": worker.days,
                    "hours_per_week": worker.hours_per_week,
                    "table_id": worker.table_id
                } for worker in all_workers],
        }
        
        return jsonify(table_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        session.close()


def convert_day_to_string(day):
    days_of_week = {
        1: "Sunday",
        2: "Monday",
        3: "Tuesday",
        4: "Wednesday",
        5: "Thursday",
        6: "Friday",
        7: "Saturday"
    }
    return days_of_week.get(day, "Unknown")

@app.route('/requirements/<int:table_id>', methods=['GET'])
@jwt_required()
@cross_origin()
def get_requirements(table_id):
    current_user = get_jwt_identity()
    session = Session()
    
    try:
        user = session.query(User).filter_by(username=current_user).first()
        if not user:
            return jsonify(msg="User not found"), 404

        # Fetch all requirements linked to the specified table_id
        requirements = session.query(Requirement).filter_by(table_id=table_id).all()

        # Prepare the data in the desired format for the client
        requirements_list = [
            {
                'id': req.id,
                'profession': req.profession,
                'day': convert_day_to_string(req.day),  # Convert day (int) to string (e.g., "Sunday")
                'hour': req.hour,
                'number': req.number_of_employees_required
            }
            for req in requirements
        ]

        session.close()
        return jsonify(requirements_list), 200

    except Exception as e:
        return jsonify(msg=str(e)), 500

@app.route('/table/<int:table_id>/workers', methods=['GET'])
@jwt_required()
@cross_origin()
def get_table_workers(table_id):
    current_user = get_jwt_identity()
    session = Session()

    try:
        user = session.query(User).filter_by(username=current_user).first()
        if not user:
            return jsonify(msg="User not found"), 404

        # Fetch the table
        table = session.query(Table).filter_by(id=table_id).first()
        if not table:
            return jsonify({'error': 'Table not found'}), 404

        # Fetch all shifts for the table
        shifts = session.query(Shift).filter_by(table_id=table_id).all()

        
        # Collect all workers linked to these shifts
        # workers_set = set()
        # for shift in shifts:
        #     for worker in shift.workers:
        #         workers_set.add(worker)
        
        workers_set = session.query(Worker).filter_by(table_id=table_id).all()

        # Convert the set of workers to a list and prepare the response data
        workers_list = [{
            "id": worker.id,
            "name": worker.name,
            "professions": worker.professions,
            "days": worker.days,
            "shifts": worker.shifts,
            "relevant_shifts_id": worker.relevant_shifts_id,
            "hours_per_week": worker.hours_per_week,
        } for worker in workers_set]

        return jsonify(workers_list), 200

    except Exception as e:
        return jsonify(msg=str(e)), 500

    finally:
        session.close()

# Function to add tables, shifts, and workers for a user
@app.route('/add_table', methods=['POST'])
@jwt_required()
@cross_origin()
def add_table():
    try: 
        current_user = get_jwt_identity()
        session = Session()
        
        # Fetch the current user from the database
        user = session.query(User).filter_by(username=current_user).first()
        if not user:
            session.close()
            return jsonify(msg="User not found"), 404

        data = request.json
        table_name = data.get('name')
        table_date = data.get('date')
        starred = data.get('starred', False)
        professions = data.get('professions', [])
        shifts_data = data.get('shifts', [])
        assignment = data.get('assignment', {})
        workers_data = data.get('workers', [])

        # Create a new table entry
        new_table = Table(
            name=table_name,
            date=table_date,
            starred=starred,
            professions=professions,
            assignment=assignment
        )
        
        session.add(new_table)
        session.commit()  # Save the table first to generate an ID

        # Add workers to the database
        worker_map = {}  # This will map worker names to their IDs
        for worker_data in workers_data:
            new_worker = Worker(
                name=worker_data['name'],
                professions=worker_data['professions'],
                days=worker_data['days'],
                hours_per_week=worker_data['hours_per_week'],
                table_id=new_table.id  # Link the worker to the new table
            )
            session.add(new_worker)
            session.flush()  # Flush to get the worker's ID without committing
            worker_map[new_worker.name] = new_worker.id  # Map worker name to ID
        
        session.commit()  # Save all workers to the database

        # Add shifts and associate workers from assignment
        for shift_data in shifts_data:
            new_shift = Shift(
                table_id=new_table.id,  # Associate the shift with the table's ID
                profession=shift_data['profession'],
                day=shift_data['day'],
                start_hour=shift_data['start_hour'],
                end_hour=shift_data['end_hour'],
                cost=shift_data['cost'],
                color=shift_data.get('color', False)
            )
            session.add(new_shift)
            session.flush()  # Flush to get the shift's ID without committing
            
            # Link workers to the shift using the assignment data
            shift_id = new_shift.id
            if str(shift_id) in assignment:
                assigned_worker_ids = assignment[str(shift_id)]
                for worker_id in assigned_worker_ids:
                    worker = session.query(Worker).filter_by(id=worker_id).first()
                    if worker:
                        new_shift.workers.append(worker)
            
            session.commit()  # Save each shift and associated workers

        # Update the user's tables array with the new table ID
        user.tablesArr = user.tablesArr + [new_table.id]
        session.commit()  # Save the updated user and table relationships

        session.close()
        return jsonify(msg="Table, shifts, and workers added successfully"), 201
    
    except Exception as e:
        return jsonify(msg=str(e)), 500
        
@app.route('/add_by_parsed_rows', methods=['POST'])
@jwt_required()
@cross_origin()
def add_by_parsed_rows():
    try:
        current_user = get_jwt_identity()
        session = Session()

        # Fetch the current user from the database
        user = session.query(User).filter_by(username=current_user).first()
        if not user:
            session.close()
            return jsonify(msg="User not found"), 404

        data = request.json

        # Parsed rows from workers.xlsx, requirements.xlsx, shifts.xlsx
        workers_data = data.get('workersData', [])
        requirements_data = data.get('requirementsData', [])
        shifts_data = data.get('shiftsData', [])


        # Create a new table
        table_name = data.get('table_name', 'New Table')
        table_date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        new_table = Table(
            name=table_name,
            date=table_date,
            starred=False,
            professions=[],
            assignment={}
        )
        session.add(new_table)
        session.commit()  # Commit to get the table ID

        # Step 1: Insert workers into the database
        worker_map = {}
        for row in workers_data:
            worker_id, name, *professions, hours_per_week, days_str = row
            days = [int(day) for day in days_str.split(',')]  # Parse days
            new_worker = Worker(
                name=name,
                professions=professions,  # List of professions
                days=days,  # List of working days
                hours_per_week=hours_per_week,
                table_id=new_table.id  # Link worker to the current table
            )
            session.add(new_worker)
            session.flush()  # Flush to get the worker's ID
            worker_map[name] = new_worker.id  # Map worker's original ID to the database ID

        session.commit()  # Commit all workers to the database

        # Step 2: Collect unique shifts
        unique_shifts = set()
        for row in shifts_data:
            profession, day, start_hour, end_hour, cost = row
            # Create a tuple to represent the unique shift
            shift_tuple = (profession, day, start_hour, end_hour, cost)
            unique_shifts.add(shift_tuple)

        # Insert unique shifts into the database
        shift_map = {}
        for shift_tuple in unique_shifts:
            profession, day, start_hour, end_hour, cost = shift_tuple
            new_shift = Shift(
                table_id=new_table.id,
                profession=profession,
                day=day,  # Day in the week (1-7)
                start_hour=start_hour,
                end_hour=end_hour,
                cost=cost,
                color=False  # You can set colors based on your project logic
            )
            session.add(new_shift)
            session.flush()  # Flush to get the shift ID
            shift_map[f"{profession}-{day}"] = new_shift.id

        session.commit()  # Commit all shifts to the database

        # Step 3: Collect unique requirements
        unique_requirements = set()
        for row in requirements_data:
            day, profession, start_hour, end_hour, num_employees = row

            # Process the requirement into hourly blocks
            temp_requirement = {
                'profession': profession,
                'day': day,
                'start_hour': start_hour,
                'end_hour': end_hour,
                'number': num_employees
            }
            processed_requirements = process_requirements([temp_requirement])

            # Add each processed requirement to the unique set
            for req in processed_requirements:
                requirement_tuple = (req['profession'], req['day'], req['hour'], req['number'])
                unique_requirements.add(requirement_tuple)

        # Insert unique requirements into the database
        for req_tuple in unique_requirements:
            profession, day, hour, num_employees = req_tuple
            new_requirement = Requirement(
                profession=profession,
                day=day,
                hour=hour,  # Store the hour from the processed result
                number_of_employees_required=num_employees,
                table_id=new_table.id  # Link requirement to the table
            )
            session.add(new_requirement)

        session.commit()  # Commit all requirements to the database

        session.commit()
        
        shifts = session.query(Shift).filter_by(table_id=new_table.id).all()
        workers = session.query(Worker).filter_by(table_id=new_table.id).all()
        requirementsArr = session.query(Requirement).filter_by(table_id=new_table.id).all()
        
        new_table.shifts = shifts
        new_table.workers = workers
        new_table.requirements = requirementsArr
        
        requirementsList = []
        shiftsList = []
        workersList = {}
        
        for requirement in requirementsArr:
            # Extract attributes from each Requirement object
            req_id = requirement.id
            profession = requirement.profession
            day = str(requirement.day)
            hour = requirement.hour
            number = requirement.number_of_employees_required
            
            # Create a dictionary with the required format
            requirement_dict = {
                'id': req_id,
                'profession': profession,
                'day': day,
                'hour': hour,
                'number': number
            }
        
            # Add the dictionary to the processed_list
            requirementsList.append(requirement_dict)
        
        for shift in shifts:
            # Extract attributes from each Shift object
            shift_id = shift.id
            profession = shift.profession
            day = str(shift.day)
            start_hour = shift.start_hour
            end_hour = shift.end_hour
            cost = shift.cost
            
            # Create a dictionary with the required format
            shift_dict = {
                'id': shift_id,
                'profession': profession,
                'day': day,
                'start_hour': start_hour,
                'end_hour': end_hour,
                'cost': cost
            }
            
            # Add the dictionary to the processed_list
            shiftsList.append(shift_dict)
        
        for worker in workers:
            # Extract attributes from each Worker object
            worker_id = worker.id
            name = worker.name
            professions = worker.professions  # Assuming this is a list of professions
            days = worker.days  # Assuming this is a list of days
            relevant_shifts_id = []
            hours_per_week = worker.hours_per_week
            
            days = [str(day) for day in days] #turn the days into strings
            
            # Create a dictionary with the required format
            worker_dict = {
                'id': worker_id,
                'name': name,
                'professions': professions,
                'days': days,
                'relevant_shifts_id': relevant_shifts_id,
                'hours_per_week': hours_per_week
            }
            
            # Add the dictionary to the processed_dict with worker_id as the key
            workersList[worker_id] = worker_dict
            
        
        # print("Shifts:", shiftsList)
        # print("Workers:", workersList)
        print("requirementsList:", requirementsList)
        
        idle_constrain = user.settings[0]
        contracts_constrain = user.settings[1]
        
        solution = get_assignment(shiftsList, workersList, requirementsList, idle_constrain, contracts_constrain)
        assignment = json_print(solution)
        
        new_table.assignment = assignment
        
        current_shifts = session.query(Shift).filter_by(table_id=new_table.id).all()

        unique_professions = set()

        for shift in current_shifts:
            unique_professions.add(shift.profession)
            if str(shift.id) in assignment:
                assigned_worker_ids = assignment[str(shift.id)]
                for w_id in assigned_worker_ids:
                    worker = session.query(Worker).filter_by(id=w_id).first()
                    if worker:
                        shift.workers.append(worker)

            session.commit()  # Save each shift and associated workers

        # After processing all the shifts, you can use the unique_professions set
        user.tablesArr = user.tablesArr + [new_table.id]
        new_table.professions = list(unique_professions)
        
        session.commit()  # Save the updated user and table relationships
        session.close()
        return jsonify(assignment), 201

    except Exception as e:
        return jsonify(msg=str(e)), 500


@app.route('/update_user_tables', methods=['POST'])
@jwt_required()
def update_user_tables():
    data = request.json
    username = data.get('username')
    tablesArr = data.get('tablesArr')
    
    session = Session()
    user = session.query(User).filter_by(username=username).first()
    
    if user:
        user.tablesArr = tablesArr
        session.commit()
        session.close()
        return jsonify(msg="User's tablesArr updated successfully")
    
    session.close()
    return jsonify(msg="User not found"), 404

@app.route('/update_assignment', methods=['POST'])
@jwt_required()
@cross_origin()
def update_assignment():
    current_user = get_jwt_identity()
    session = Session()
    
    try:
        user = session.query(User).filter_by(username=current_user).first()
        if not user:
            return jsonify(msg="User not found"), 404

        # Extract the data from the request
        data = request.json
        tableId = data.get('tableId')
        new_assignment = data.get('assignment')
        new_shifts_data = data.get('shifts', [])

        if not tableId:
            return jsonify(msg="Invalid data"), 400

        # Find the table with the provided tableId
        table = session.query(Table).filter_by(id=tableId).first()

        if not table:
            return jsonify(msg="Table not found"), 404

        # Update the assignment field
        table.assignment = new_assignment

        # Update existing shifts and workers associated with the table
        existing_shifts = session.query(Shift).filter_by(table_id=table.id).all()
        existing_workers = session.query(Worker).filter_by(table_id=table.id).all()

        # Clear existing worker-shift relationships
        for shift in existing_shifts:
            shift.workers.clear()

        # Update shifts and associate workers from the new assignment
        worker_map = {worker.id: worker for worker in existing_workers}

        for shift_data in new_shifts_data:
            shift = session.query(Shift).filter_by(id=shift_data['id'], table_id=table.id).first()

            if shift:
                # Update shift details if needed
                shift.profession = shift_data['profession']
                shift.day = shift_data['day']
                shift.start_hour = shift_data['start_hour']
                shift.end_hour = shift_data['end_hour']
                shift.cost = shift_data['cost']
                shift.color = shift_data.get('color', shift.color)

                # Associate workers based on the new assignment
                shift_id = shift.id
                if str(shift_id) in new_assignment:
                    assigned_worker_ids = new_assignment[str(shift_id)]
                    for worker_id in assigned_worker_ids:
                        worker = worker_map.get(worker_id)
                        if worker:
                            shift.workers.append(worker)
                session.add(shift)
        
        session.commit()

        return jsonify(msg="Assignment, shifts, and workers updated successfully"), 200

    except Exception as e:
        session.rollback()
        return jsonify(msg=str(e)), 500

    finally:
        session.close()


# Function to update the table name
@app.route('/update_table_name/<int:table_id>', methods=['PUT'])
@jwt_required()
@cross_origin()
def update_table_name(table_id):
    try:
        current_user = get_jwt_identity()
        session = Session()
        
        # Fetch the current user from the database
        user = session.query(User).filter_by(username=current_user).first()
        if not user:
            session.close()
            return jsonify(msg="User not found"), 404

        # Fetch the table associated with the table_id and current user
        table = session.query(Table).filter_by(id=table_id).first()
        if not table:
            session.close()
            return jsonify(msg="Table not found"), 404
        
        # Get new table name from the request
        data = request.json
        new_name = data.get('name')
        if not new_name:
            session.close()
            return jsonify(msg="New table name is required"), 400
        
        if len(new_name) > 50:
            session.close()
            return jsonify(msg="Table name is too long"), 400

        # Update the table name
        table.name = new_name
        session.commit()

        session.close()
        return jsonify(msg="Table name updated successfully"), 200
    
    except Exception as e:
        return jsonify(msg=str(e)), 500


@app.route('/toggle_star/<int:table_id>', methods=['POST'])
@jwt_required()
@cross_origin()
def toggle_star(table_id):
    current_user = get_jwt_identity()
    session = Session()
    data = request.json
    # table_id = data.get('table_id')
    
    try:
        # Fetch the table to be toggled
        table = session.query(Table).filter_by(id=table_id).first()
        if not table:
            return jsonify(msg="Table not found"), 404

        # Toggle the star value
        table.starred = not table.starred
        session.commit()
        
        return jsonify(msg="Star status toggled successfully", starred=table.starred), 200
    
    except Exception as e:
        return jsonify(msg=str(e)), 500
    
    finally:
        session.close()

@app.route('/delete_table/<int:table_id>', methods=['DELETE'])
@jwt_required()
@cross_origin()
def delete_table(table_id):
    current_user = get_jwt_identity()
    session = Session()
    
    user = session.query(User).filter_by(username=current_user).first()
    if not user:
        session.close()
        return jsonify(msg="User not found"), 404    
    
    try:
        # Fetch the table to be deleted
        table = session.query(Table).filter_by(id=table_id).first()
        if not table:
            return jsonify(msg="Table not found"), 404

        # Remove the table and associated shifts
        session.delete(table)
        session.commit()

        return jsonify(msg="Table and associated data deleted successfully"), 200
    
    except Exception as e:
        return jsonify(msg=str(e)), 500
    
    finally:
        session.close()


@app.route('/update-settings', methods=['POST'])
@jwt_required()  # Ensure the user is logged in
def update_settings():
    data = request.json
    username = data.get('username')
    settings = data.get('settings')
    
    session = Session()
    user = session.query(User).filter_by(username=username).first()
    
    if user:
        user.settings = settings
        session.commit()
        session.close()
        return jsonify(msg="User's settings updated successfully")
    
    session.close()
    return jsonify(msg="User not found"), 404

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    
    user = fetch_user_from_db(username)
    
    if user and user.check_password(password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token)
    
    return jsonify(msg="Invalid credentials"), 401

@app.route('/register', methods=['POST'])
@cross_origin()
def register():
    session = Session()
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify(msg="Username and password are required"), 400

        existing_user = session.query(User).filter_by(username=username).first()
        if existing_user:
            return jsonify(msg="Username already taken"), 409

        # Generate a random color for the user
        color_list = ["blue", "orange", "yellow", "pink", "brown", "white", "purple", "green"]
        user_color = random.choice(color_list)

        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        # Create a new user
        new_user = User(
            username=username,
            password=hashed_password,
            color=user_color,
            tablesArr=[],
            picture="",
            settings=[False, False]
        )

        session.add(new_user)
        session.commit()

        # Optionally, create a JWT token to log in the user immediately after registration
        access_token = create_access_token(identity=username)

        return jsonify(msg="User registered successfully", token=access_token), 201

    except Exception as e:
        session.rollback()
        return jsonify(msg=str(e)), 500

    finally:
        session.close()


@app.route('/login/google', methods=['POST'])
def login_google():
    data = request.json
    user_google_id = data.get("sub")
    user_email = data.get("email")
    user_name = data.get("name")
    user_picture = data.get("picture")

    session = Session()
    user = session.query(User).filter_by(email=user_email).first()
    
    hashed_password = generate_password_hash(user_google_id)
    
    if not user:
        # Register a new user
        color_list = ["#f5f3f6", "#178f36", "#ff577a", "#f5af69", "#dfe685", "#81d6c9", "#7fb8e3"]
        user_color = random.choice(color_list)
        user = User(
            username=user_name,
            password=hashed_password,
            email=user_email,
            color=user_color,
            tablesArr=[],
            picture=user_picture,
            settings=[False, False],
            google_id=user_google_id,
        )
        session.add(user)
        session.commit()

    # Log in the user by creating a JWT before closing the session
    access_token = create_access_token(identity=user.username)

    session.close()  # Close session after all operations are complete

    return jsonify(msg="Logged in with Google", token=access_token), 200


@app.route('/get_current_user', methods=['GET'])
@jwt_required()
@cross_origin()
def get_current_user():
    session = Session()
    try:
        current_user = get_jwt_identity()
        
        # Fetch the user from the database
        user = session.query(User).filter_by(username=current_user).first()
        
        if not user:
            return jsonify(msg="User not found"), 404
        
        # Prepare the user data to return
        user_data = {
            'username': user.username,
            'color': user.color,
            'tablesArr': user.tablesArr,
            'settings': user.settings
        }
        
        return jsonify(user_data=user_data), 200

    except Exception as e:
        return jsonify(msg=str(e)), 500

    finally:
        session.close()

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    session = Session()
    user = session.query(User).filter_by(username=current_user).first()
    session.close()  # Close session
    if user:
        return jsonify(current_user=current_user)
    return jsonify(msg="User not found"), 404

        
        
if __name__ == '__main__':
    app.run()
