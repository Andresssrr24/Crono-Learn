from .models import *
from .session import engine
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass