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
        ref=body["ref"],
        after=body["after"],
        before=body["before"],
        state = "QUEUE"
      )
      db.session.add(data_insert)
      db.session.commit()

  def select_test(self, key, value, return_key=None):
    with DBConnectionHandler() as db:
      data = db.session.query(Tasks).filter(getattr(Tasks, key) == value).first()
      if not data:
        return None
      elif return_key == None:
        return data
      else:
        return getattr(data, return_key)

  def delete(self, id):
    with DBConnectionHandler() as db:
      data_delete = db.session.query(Tasks).filter(Tasks.id == id).first()
      data_delete.delete()
      db.session.commit()

  def update(self, key, value, **body):
    with DBConnectionHandler() as db:
      data = db.session.query(Tasks).filter(getattr(Tasks, key) == value).first()
      for key1, value1 in body.items():
        setattr(data, key1, value1)
      db.session.commit()
