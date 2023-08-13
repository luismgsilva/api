from infra.configs.connection import DBConnectionHandler
from infra.entities.tasks import Tasks

class TasksRepository:
  def select(self):
    with DBConnectionHandler() as db:
      data = db.session.query(Tasks).all()
      return data

  def insert(self, **body):
    with DBConnectionHandler() as db:
      print(body)
      data_insert = Tasks(
        repository_name=body["repository_name"],
        pusher_name=body["pusher_name"],
        state = "QUEUE"
      )
      db.session.add(data_insert)
      db.session.commit()

  def search_by_state(self, state):
    with DBConnectionHandler() as db:
      data_search_by_state = db.session.query(Tasks).filter(Tasks.state == state).first()
      return data_search_by_state

  def search_by_id(self, id):
    with DBConnectionHandler() as db:
      data_search_by_id = db.session.query(Tasks).filter(Tasks.id == id).first()
      return data_search_by_id

  def delete(self, id):
    with DBConnectionHandler() as db:
      data_delete = db.session.query(Tasks).filter(Tasks.id == id).first()
      data_delete.delete()
      db.session.commit()

  def update(self, id, **body):
    with DBConnectionHandler() as db:
      # data_update = db.session.query(Tasks).filter(Tasks.id == id).first()
      for key, value in body.items():
        db.session.query(Tasks).filter(Tasks.id == id).update({key: value})
      db.session.commit()

  # not sure
  def get_data(self, id, key):
    with DBConnectionHandler() as db:
      data_select = db.session.query(Tasks).filter(Tasks.id == id).first()
      return getattr(data_select, key)


