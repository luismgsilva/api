from infra.configs.base import Base
from sqlalchemy import Column, String, Integer, Enum

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


