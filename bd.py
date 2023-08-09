from sqlalchemy import create_engine, Column, Integer, String, Sequence, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the database connection
DATABASE_URL = "sqlite:///mydatabase.db"
engine = create_engine(DATABASE_URL, echo=True)
SessionsLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative models
Base = declarative_base()

class StateMachine(Base):
    __tablename__ = "state_machine"

    id = Column(Integer, primary_key=True)
    machine = Column(String)
    state = Column(Enum("FREE", "PENDING" ,"EXECUTING", "MAINTENANCE", name="machine_state_enum"))
    # task = Column(Integer) -> task ID being processed.

    process_id = Column(String)

class Tasks(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    ref = Column(String)
    before = Column(String)
    after = Column(String)
    repository_name = Column(String)
    repository_full_name = Column(String)
    pusher_name = Column(String)
    commit_id = Column(String)
    commit_message = Column(String)
    # commit_timestamp = Column(DateTime)
    commit_url = Column(String)
    commit_author_name = Column(String)
    commit_author_email = Column(String)

    state = Column(Enum("PENDING", "EXECUTING", "PASSED", "FAILED", name="task_state_enum"))
    state_machine_id = Column(Integer, ForeignKey('state_machine.id'), unique=True)
    # state_machine_id = Column(Integer)

# Create the database tables
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    db = SessionsLocal()
    new_machine = StateMachine(machine="localhost", state="FREE")
    db.add(new_machine)
    db.commit()