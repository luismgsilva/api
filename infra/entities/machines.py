from infra.configs.base import Base
from sqlalchemy import Column, String, Integer, Enum

class Machines(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True)
    machine = Column(String)
    state = Column(Enum("AVAILABLE", "PENDING" ,"RUNNING", "MAINTENANCE", name="machine_state_enum"))


