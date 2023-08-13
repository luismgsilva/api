from infra.configs.base import Base
from sqlalchemy import Column, String, Integer, Enum, ForeignKey

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
#    ref = Column(String)
#    before = Column(String)
#    after = Column(String)
    repository_name = Column(String)
#    repository_full_name = Column(String)
    pusher_name = Column(String)
#    commit_id = Column(String)
#    commit_message = Column(String)
    # commit_timestamp = Column(DateTime)
#    commit_url = Column(String)
#    commit_author_name = Column(String)
#    commit_author_email = Column(String)

    # state = Column(TaskState, name="task_state_enum")
    state = Column(Enum("QUEUE", "PENDING", "EXECUTING", "PASSED", "FAILED", "KILLED", name="task_state_enum"))
    process_id = Column(Integer) # -> task ID being processed.
    machine_id = Column(Integer, ForeignKey("machines.id"), unique=True)