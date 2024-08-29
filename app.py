from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS, cross_origin
from models import User, Table, Shift
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
        # Fetch the user from the database
        user = session.query(User).filter_by(username=current_user).first()
        if not user:
            return jsonify(msg="User not found"), 404
        
        # Get the user's tables IDs
        table_ids = user.tablesArr
        
        # Fetch the tables from the database
        tables = session.query(Table).filter(Table.name.in_(table_ids)).all()
        
        # Convert tables to a list of dictionaries
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
                "id_list": shift.id_list,
                "color": shift.color
            } for shift in table.shifts],
            "assignment": table.assignment
        } for table in tables]
        
        return jsonify(tables_list)
    
    except Exception as e:
        return jsonify(msg=str(e)), 500
    
    finally:
        session.close()

# Function to add tables and shifts for a user
@app.route('/add_table', methods=['POST'])
@jwt_required()
@cross_origin()
def add_table():
    current_user = get_jwt_identity()
    session = Session()
    
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

    new_table = Table(
        name=table_name,
        date=table_date,
        starred=starred,
        professions=professions,
        assignment=assignment
    )
    
    session.add(new_table)
    session.commit()  # Save the table first to generate an ID

    # Add shifts associated with this table
    for shift_data in shifts_data:
        new_shift = Shift(
            table_id=new_table.id,  # Associate the shift with the table's ID
            profession=shift_data['profession'],
            day=shift_data['day'],
            start_hour=shift_data['startHour'],
            end_hour=shift_data['endHour'],
            cost=shift_data['cost'],
            id_list=shift_data.get('idList', []),
            color=shift_data.get('color', "")
        )
        session.add(new_shift)

    session.commit()  # Save all shifts to the database
    session.close()
    
    return jsonify(msg="Table and shifts added successfully"), 201


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
