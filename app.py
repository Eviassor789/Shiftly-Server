from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS, cross_origin
from models import User, Table, Shift, Worker
from base import Session, create_tables

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)

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
create_test_user("killua", "kkk", [], "", [True, False], "#f5f3f6")

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
                "day": shift.day,
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
                "day": shift.day,
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

        if not tableId or not new_assignment:
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



@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    
    user = fetch_user_from_db(username)
    
    if user and user.check_password(password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token)
    
    return jsonify(msg="Invalid credentials"), 401

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
