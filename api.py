from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
import paho.mqtt.client as mqtt

from bd import StateMachine, Tasks

# Define the database connection
DATABASE_URL = "sqlite:///mydatabase.db"
engine = create_engine(DATABASE_URL, echo=True)
SessionsLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

# Pydantic model for the item
class WebhookPayload(BaseModel):
    ref: str
    before: str
    after: str
    repository: dict
    pusher: dict
    commits: list

# Define a base class for declarative models
Base = declarative_base()

@app.post("/webhook")
def webhook_handler(payload: WebhookPayload):
    try:

        db_payload = Tasks(
            ref=payload.ref,
            before=payload.before,
            after=payload.after,
            repository_name=payload.repository["name"],
            repository_full_name=payload.repository["full_name"],
            pusher_name=payload.pusher["name"],
            commit_id=payload.commits[0]["id"],
            commit_message=payload.commits[0]["message"],
            # commit_timestamp=datetime.strptime(payload.commits[0]["timestamp"], "%Y-%m-%dT%H:%M:%SZ"),
            commit_url=payload.commits[0]["url"],
            commit_author_name=payload.commits[0]["author"]["name"],
            commit_author_email=payload.commits[0]["author"]["email"],

            state = "PENDING"
        )

        db = SessionsLocal()
        db.add(db_payload)
        db.commit()
        db.refresh(db_payload)

        free_machines = db.query(StateMachine).filter_by(state='FREE').all()

        if free_machines:
            machine = free_machines[0]
            machine.state = 'PENDING'

            pending_task = db.query(Tasks).filter_by(state="PENDING").first()

            # WRONG - JUST FOR TESTING
            pending_task.state_machine_id = machine.id

            db.commit()

            # Publishes a message to an MQTT broker
            publish_to_mqtt("webhook_data", pending_task.id)

        db.close()

        # Write payload to file for debug purposes
        debug(payload)

        return db_payload

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error processing webhook")

# Get all tasks
@app.get("/tasks")
def read_data(skip: int = 0, limit: int = 10):
    try:
        db = SessionsLocal()
        data = db.query(Tasks).offset(skip).limit(limit).all()
        db.close()
        return data

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error processing webhook")

@app.put("/task/")
def read_data(id: int, data: dict):
    try:
        db = SessionsLocal()
        print(id)
        task = db.query(Tasks).filter_by(id=id).first()
        task.state = data["state"]
        tmp = task.state_machine_id
        machine = db.query(StateMachine).filter_by(id=tmp).first()
        machine.state = 'FREE'
        db.commit()

        db.close()
        return task

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error processing webhook")


# Update one task
@app.get("/task/")
def read_data(id: int):
    try:
        db = SessionsLocal()
        task = db.query(Tasks).filter_by(id=id).first()
        free_machines = db.query(StateMachine).filter_by(state='PENDING').all()
        machine = free_machines[0]
        task.state = 'EXECUTING'
        machine.state = 'EXECUTING'
        db.commit()

        db.close()
        return task

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error processing webhook")


# Get all machines
@app.get("/machines")
def read_data(skip: int = 0, limit: int = 10):
    try:
        db = SessionsLocal()
        data = db.query(StateMachine).offset(skip).limit(limit).all()
        db.close()
        return data

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error processing webhook")


# Hello World
@app.get("/")
async def root():
    return {"message": "Hello World"}

# from sqlalchemy import event
# @event.listens_for(WebhookPayloadCreate, "before_insert")
# def before_insert_listener(mapper, connection, target):
#     print("funciona before insert: ", target.id)
#     publish_to_mqtt("webhook_data", target.repository_name)

# session = SessionsLocal()
# @event.listens_for(session, "after_commit")
# def after_commit_listener(session):
#     print("funciona after commit.")

# Publishes a message to an MQTT broker
def publish_to_mqtt(topic, payload):
    mqtt_broker = "localhost"
    mqtt_port = 1883
    mqtt_client = mqtt.Client()

    try:
        mqtt_client.connect(mqtt_broker, mqtt_port)
        mqtt_client.publish(topic, payload)
        mqtt_client.disconnect()
    except Exception as e:
        print("Error publishing to MQTT:", str(e))

# Write payload to file for debug purposes
import json
def debug(payload: WebhookPayload):
    file_path = "webhook.json"
    with open(file_path, 'w') as json_file:
        json.dump(payload.dict(), json_file, indent=4)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)