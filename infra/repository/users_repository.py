from infra.configs.connection import DBConnectionHandler
from sqlalchemy.orm import joinedload
from infra.entities.users import Users

class UsersRepository:
  def select(self):
    with DBConnectionHandler() as db:
      data = db.session.query(Users).all()
      return data

  def insert(self, **body):
    with DBConnectionHandler() as db:
      print(body)
      data_insert = Users(**body)
      db.session.add(data_insert)
      db.session.commit()

      return data_insert.id

  def select_test(self, key, value, return_key=None):
    with DBConnectionHandler() as db:
      data = db.session.query(Users).filter(getattr(Users, key) == value).first()
      if not data:
        return None
      elif return_key == None:
        return data
      else:
        return getattr(data, return_key)

  def delete(self, id):
    with DBConnectionHandler() as db:
      data = db.session.query(Users).filter(Users.id == id).first()
      data.delete()
      db.session.commit()

  def update(self, key, value, **body):
    with DBConnectionHandler() as db:
      data = db.session.query(Users).filter(getattr(Users, key) == value).first()
      for key1, value1 in body.items():
        setattr(data, key1, value1)
      db.session.commit()