import sqlalchemy as sa

from sqlalchemy import create_engine

from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash

# Set up the database engine and session
engine = sa.create_engine('sqlite:///users.db', echo=False)
Session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    tablesArr = Column(JSON, default=[])
    picture = Column(String, default="")
    settings = Column(JSON, default=[False, True])
    color = Column(String, default="#178f36")

    def set_password(self, secret):
        self.password = generate_password_hash(secret)

    def check_password(self, secret):
        return check_password_hash(self.password, secret)

# def reset_database():
#     engine = create_engine('sqlite:///users.db')
#     Base.metadata.drop_all(engine)  # Drop all tables
#     Base.metadata.create_all(engine)  # Create new tables

# reset_database()

# Create tables
Base.metadata.create_all(engine)
