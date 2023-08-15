from infra.configs.base import Base
from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    is_superuser = Column(Boolean)
    is_active = Column(Boolean)
    name = Column(String)
    password = Column(String)
    email_address = Column(String)

    permissions = Column(String(64))

    # permissions = relationship('Permissions', secondary='user_permission', back_populates='users')
    # roles = relationship('Roles', secondary='user_role', back_populates='users')

