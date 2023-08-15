from infra.configs.base import Base
from sqlalchemy import Column, String, Integer, Enum, ForeignKey, JSON

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
    ref = Column(String)
    before = Column(String)
    after = Column(String)
    repository_name = Column(String)
#    repository_full_name = Column(String)
    pusher_name = Column(String)
#    commit_id = Column(String)
#    commit_message = Column(String)
    # commit_timestamp = Column(DateTime)
#    commit_url = Column(String)
#    commit_author_name = Column(String)
#    commit_author_email = Column(String)

    notes = Column(JSON)
    # # msg=$(git -C /home/luis/work/bsf/testing-gcc-parallel/.bsf log -n 1 --skip=2 --pretty=%B)
    #commit_hash=$(git -C /home/luis/work/bsf/testing-gcc-parallel/.bsf log --skip=2 -n 1 --pretty=format:"%H")
    #commit_message=$(git -C /home/luis/work/bsf/testing-gcc-parallel/.bsf  log --skip=2 -n 1 --pretty=format:"%B")
    #msg="{ \"hash\": \"$commit_hash\", \"msg\": $commit_message }"
    #body="{ \"task_id\": \"1\", \"exit_code\": $msg }"
    #curl -X POST -H "Content-Type: application/json" -d "$body" "$url"


    # state = Column(TaskState, name="task_state_enum")
    state = Column(Enum("QUEUE", "PENDING", "EXECUTING", "PASSED", "FAILED", "KILLED", name="task_state_enum"))
    process_id = Column(Integer) # -> task ID being processed.
    machine_id = Column(Integer, ForeignKey("machines.id"), unique=True)