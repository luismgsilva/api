from infra.configs.connection import DBConnectionHandler
from infra.entities.machines import Machines

class MachinesRepository:
  def select(self):
    with DBConnectionHandler() as db:
      print("ola")
      data = db.session.query(Machines).all()
      return data

  def insert(self, **body):
    with DBConnectionHandler() as db:
      data_insert = Machines(**body)
      db.session.add(data_insert)
      db.session.commit()

  def select_test(self, key, value, return_key=None):
    with DBConnectionHandler() as db:
      data = db.session.query(Machines).filter(getattr(Machines, key) == value).first()
      if not data:
        return None
      elif return_key == None:
        return data
      else:
        return getattr(data, return_key)

  def delete(self, id):
    with DBConnectionHandler() as db:
      data_delete = db.session.query(Machines).filter(Machines.id == id)
      data_delete.delete()
      db.session.commit()

  def update(self, key, value, **body):
    with DBConnectionHandler() as db:
      data = db.session.query(Machines).filter(getattr(Machines, key) == value).first()
      for key1, value1 in body.items():
        setattr(data, key1, value1)
      db.session.commit()
