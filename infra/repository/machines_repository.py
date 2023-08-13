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

  def search_by_state(self, state):
    with DBConnectionHandler() as db:
      data_search_by_state = db.session.query(Machines).filter(Machines.state == state).first()
      return data_search_by_state

  def delete(self, id):
    with DBConnectionHandler() as db:
      data_delete = db.session.query(Machines).filter(Machines.id == id)
      data_delete.delete()
      db.session.commit()

  def update(self, id, **body):
    with DBConnectionHandler() as db:
      data_update = db.session.query(Machines).filter(Machines.id == id)
      for key, value in body.items():
        data_update.update({key: value})
      db.session.commit()
