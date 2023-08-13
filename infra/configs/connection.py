from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class DBConnectionHandler:
  def __init__(self):
    self.__connection_string = "sqlite:///mydatabase.db"
    self.__engine = self.__create_database_engine()
    self.session = None

  def __create_database_engine(self):
    engine = create_engine(self.__connection_string, echo=True)
    return engine

  def get_engine(self):
    return self.__engine

  def __enter__(self):
    session_make = sessionmaker(autocommit=False, autoflush=False, bind=self.get_engine())
    self.session = session_make()
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    self.session.close()