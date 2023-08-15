from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Define the database connection
DATABASE_URL = "sqlite:///mydatabase.db"
engine = create_engine(DATABASE_URL, echo=True)
SessionsLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from infra.entities.machines import Machines
from infra.entities.tasks import Tasks
from infra.entities.users import Users

# Create the database tables
Machines.metadata.create_all(engine)
Tasks.metadata.create_all(engine)
Users.metadata.create_all(engine)

