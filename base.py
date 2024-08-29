import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up the database engine and session
engine = sa.create_engine('sqlite:///users.db', echo=False)
Session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()

# Create tables
def create_tables():
    Base.metadata.create_all(engine)
