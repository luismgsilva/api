from infra.configs.connection import DBConnectionHandler
from infra.entities.users import Users

class UsersRepository:
  def select(self):
    with DBConnectionHandler() as db:
      data = db.session.query(Users).all()
      return data

  def insert(self, **body):
    with DBConnectionHandler() as db:
      print(body)
      data_insert = Users(
          name = body["name"],
          password = body["password"],
          permission = body["permission"]
      )
      db.session.add(data_insert)
      db.session.commit()

  def select_by_id(self, id):
    with DBConnectionHandler() as db:
      data_select_by_id = db.session.query(Users).filter(Users.id == id).first()
      return data_select_by_id

  def select_by_name(self, name):
    with DBConnectionHandler() as db:
      data_select_by_id = db.session.query(Users).filter(Users.name == name).first()
      return data_select_by_id

  def delete(self, id):
    with DBConnectionHandler() as db:
      data_delete = db.session.query(Users).filter(Users.id == id).first()
      data_delete.delete()
      db.session.commit()

  def update(self, id, **body):
    with DBConnectionHandler() as db:
      data_update = db.session.query(Users).filter(Users.id == id).first()
      for key, value in body.items():
        data_update.update({key: value})
      db.session.commit()

  # not sure
  def search_by_id(self, id, key):
    with DBConnectionHandler() as db:
      data_search_by_id = db.session.query(Users).filter(Users.id == id).first()
      return getattr(data_search_by_id, key)

  def search_by_name(self, name, key):
    with DBConnectionHandler() as db:
      data_search_by_name = db.session.query(Users).filter(Users.name == name).first()
      return getattr(data_search_by_name, key)


