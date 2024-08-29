from sqlalchemy import Column, Integer, String, Boolean, JSON, ForeignKey, create_engine
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from base import Base, Session

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

class Table(Base):
    __tablename__ = 'tables'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    date = Column(String, nullable=False)
    starred = Column(Boolean, default=False)
    professions = Column(JSON, default=[])
    shifts = relationship('Shift', backref='table', cascade="all, delete-orphan")
    assignment = Column(JSON, default={})

class Shift(Base):
    __tablename__ = 'shifts'

    id = Column(Integer, primary_key=True)
    table_id = Column(Integer, ForeignKey('tables.id'), nullable=False)
    profession = Column(String, nullable=False)
    day = Column(String, nullable=False)
    start_hour = Column(String, nullable=False)
    end_hour = Column(String, nullable=False)
    cost = Column(Integer, nullable=False)
    id_list = Column(JSON, default=[])
    color = Column(Boolean, default=False)

# def reset_database():
#     engine = create_engine('sqlite:///users.db')
#     Base.metadata.drop_all(engine)  # Drop all tables
#     Base.metadata.create_all(engine)  # Create new tables

# reset_database()
