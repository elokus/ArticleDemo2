from database.models import *
from sqlmodel import SQLModel, create_engine
import os


# local stored database
DATABASE_URL = r"sqlite:///app.db"

# in-memory database for testing
TEST_DATABASE_URL = "sqlite:///test.db"

engine = create_engine(DATABASE_URL, echo=False) \
    if os.getenv("ENV") != "test" else create_engine(TEST_DATABASE_URL, echo=False)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


create_db_and_tables()
