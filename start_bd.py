from sqlalchemy import create_engine, Column, Integer, String, Sequence, Enum, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the database connection
DATABASE_URL = "sqlite:///mydatabase.db"
engine = create_engine(DATABASE_URL, echo=True)
SessionsLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative models
Base = declarative_base()

class TaskState(Enum):
    QUEUE = "QUEUE"
    PENDING = "PENDING"
    EXECUTING = "EXECUTING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    KILLED = "KILLED"

class Tasks(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    repository_name = Column(String)
    pusher_name = Column(String)
    # state = Column(TaskState, name="task_state_enum")
    state = Column(Enum("QUEUE", "PENDING", "EXECUTING", "PASSED", "FAILED", "KILLED", name="task_state_enum"))
    process_id = Column(Integer) # -> task ID being processed.
    machine_id = Column(Integer, ForeignKey("machines.id"), unique=True)


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    is_superuser = Column(Boolean)
    is_active = Column(Boolean)
    name = Column(String)
    password = Column(String)
    email_address = Column(String)
    web_token = Column(String)

    # delete
    permission = Column(String)

class MachineState(Enum):
  AVAILABLE = "AVAILABLE"
  PENDING = "PENDING"
  RUNNING = "RUNNING"
  MAINTENANCE = "MAINTENANCE"

class Machines(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True)
    machine = Column(String)
    # state = Column(MachineState, name="machine_state_enum")
    state = Column(Enum("AVAILABLE", "PENDING" ,"RUNNING", "MAINTENANCE", name="machine_state_enum"))


# Create the database tables
Base.metadata.create_all(bind=engine)
