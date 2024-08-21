from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import Session, User
from flask_cors import CORS

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
jwt = JWTManager(app)

CORS(app)  # Enable CORS for all routes
    
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
create_test_user("killua", "kkk", [211, 212], "", [True, False], "#f5f3f6")

def fetch_user_from_db(username):
    session = Session()
    user = session.query(User).filter_by(username=username).first()
    session.close()  # Close session
    return user

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
