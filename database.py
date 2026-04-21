# set up the database connection

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

"""
1. Tell SQLAlchemy where the database file lives
2. Create an engine — the actual connection to the database
3. Create a session — how your code talks to the database per request
4. Create a base class — all your models (tables) will inherit from this
"""
SQLALCHEMY_DATABASE_URL = "sqlite:///./musicme.db"
# engine is connection to database musicme.db
engine = create_engine(SQLALCHEMY_DATABASE_URL)
# session is how we interact with db per request
SessionLocal = sessionmaker(bind=engine)
# base class that db models from:
Base = declarative_base()