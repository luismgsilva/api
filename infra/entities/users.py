from infra.configs.base import Base
from sqlalchemy import Column, String, Integer, Boolean

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
