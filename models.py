# defines your tables as Python classes

from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class Favourite(Base):
    __tablename__ = "favourites"
    id = Column(Integer, primary_key=True)
    track_name = Column(String)
    artist = Column(String)
    saved_at = Column(DateTime, default=datetime.now)

class History(Base):
    __tablename__ = "history"
    id = Column(Integer, primary_key=True)
    track_name = Column(String)
    artist = Column(String)
    searched_at = Column(DateTime, default=datetime.now)
