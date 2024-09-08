from sqlalchemy import Column, Integer, String, Boolean, JSON, ForeignKey, create_engine
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from base import Base, Session
from sqlalchemy import Table as SQLAlchemyTable

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    tablesArr = Column(JSON, default=[])
    picture = Column(String, default="")
    settings = Column(JSON, default=[False, True])
    color = Column(String, default="#178f36")
    email = Column(String, nullable=True, unique=True)
    google_id = Column(String, nullable=True, unique=True)
    
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
    assignment = Column(JSON, default={})
    
    shifts = relationship('Shift', backref='table', cascade="all, delete-orphan")
    workers = relationship('Worker', backref='table', cascade="all, delete-orphan")
    requirements = relationship('Requirement', backref='table', cascade="all, delete-orphan")


class Shift(Base):
    __tablename__ = 'shifts'

    id = Column(Integer, primary_key=True)
    table_id = Column(Integer, ForeignKey('tables.id'), nullable=False)
    profession = Column(String, nullable=False)
    day = Column(String, nullable=False)
    start_hour = Column(String, nullable=False)
    end_hour = Column(String, nullable=False)
    cost = Column(Integer, nullable=False)
    color = Column(String, default=False)
    
    # Relationship to link shifts to workers
    workers = relationship('Worker', secondary='worker_shifts', back_populates='shifts')


class Worker(Base):
    __tablename__ = 'workers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    professions = Column(JSON, default=[])
    days = Column(JSON, default=[])
    hours_per_week = Column(Integer, nullable=False)
    table_id = Column(Integer, ForeignKey('tables.id'), nullable=False)

    shifts = relationship('Shift', secondary='worker_shifts', back_populates='workers')


# New Requirement class based on your specification
class Requirement(Base):
    __tablename__ = 'requirements'

    id = Column(Integer, primary_key=True)
    profession = Column(String, nullable=False)
    day = Column(Integer, nullable=False)  # Day in the week (1-7)
    start_hour = Column(String, nullable=False)
    end_hour = Column(String, nullable=False)
    number_of_employees_required = Column(Integer, nullable=False)
    
    table_id = Column(Integer, ForeignKey('tables.id'), nullable=False)  # Link to the Table


# Association table for many-to-many relationship between Worker and Shift
worker_shifts = SQLAlchemyTable('worker_shifts', Base.metadata,
    Column('worker_id', Integer, ForeignKey('workers.id'), primary_key=True),
    Column('shift_id', Integer, ForeignKey('shifts.id'), primary_key=True)
)


def reset_database():
    engine = create_engine('sqlite:///users.db')
    Base.metadata.drop_all(engine)  # Drop all tables
    Base.metadata.create_all(engine)  # Create new tables

reset_database()
