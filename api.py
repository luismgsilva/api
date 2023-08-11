import paho.mqtt.client as mqtt
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from bd import StateMachine, Tasks
from pydantic import BaseModel
import json
from datetime import datetime
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Publishes a message to an MQTT broker
def publish_to_mqtt(topic, payload):
    mqtt_broker = "localhost"
    mqtt_port = 1883
    mqtt_client = mqtt.Client()
    payload = json.dumps(payload)

    try:
        mqtt_client.connect(mqtt_broker, mqtt_port)
        mqtt_client.publish(topic, payload)
        mqtt_client.disconnect()
    except Exception as e:
        logger.error("Error publishing to MQTT: %s", str(e))

# Write payload to a file for debug purposes
def debug(payload: WebhookPayload):
    file_path = "webhook.json"
    with open(file_path, 'w') as json_file:
        json.dump(payload.dict(), json_file, indent=4)

def task_handler():

    try:
        with SessionsLocal() as db:
            # Do I do a new search for a available server?
            pending_task = db.query(Tasks).filter_by(state="QUEUE").first()
            machine = db.query(StateMachine).filter_by(state='FREE').first()
            if pending_task and machine:
                pending_task.state = "PENDING"
                machine.state = "PENDING"
                pending_task.state_machine_id = machine.id
                db.commit()

                publish_to_mqtt("start_task", { "task_id": pending_task.id } )

    except Exception as e:
        logger.exception("Error processing task_handler")
        raise HTTPException(status_code=500, detail="Error processing task_handler")

# Process webhook payload
@app.post("/webhook")
def webhook_handler(payload: WebhookPayload):
    try:

        with SessionsLocal() as db:

            db_payload = Tasks(
                ref=payload.ref,
                before=payload.before,
                after=payload.after,
                repository_name=payload.repository["name"],
                repository_full_name=payload.repository["full_name"],
                pusher_name=payload.pusher["name"],
                commit_id=payload.commits[0]["id"],
                commit_message=payload.commits[0]["message"],
                commit_url=payload.commits[0]["url"],
                commit_author_name=payload.commits[0]["author"]["name"],
                commit_author_email=payload.commits[0]["author"]["email"],
                state = "QUEUE"
            )

            db.add(db_payload)
            db.commit()
            # db.refresh(db_payload)


            task_handler()
            # free_machines = db.query(StateMachine).filter_by(state='FREE').all()
            # if free_machines:
                # machine = free_machines[0]
                # machine.state = 'PENDING'

                # pending_task = db.query(Tasks).filter_by(state="QUEUE").first()
                # pending_task.state_machine_id = machine.id

                # db.commit()

                # # Publishes a message to an MQTT broker
                # publish_to_mqtt("start_task", { "task_id": pending_task.id } )

        return db_payload

    except Exception as e:
        logger.exception("Error processing webhook: %s", str(e))
        raise HTTPException(status_code=500, detail="Error processing webhook")

# Get all tasks
@app.get("/tasks")
def read_data(skip: int = 0, limit: int = 10):
    try:
        with SessionsLocal() as db:
            data = db.query(Tasks).offset(skip).limit(limit).all()

        return data

    except Exception as e:
        logger.exception("Error getting tasks: %s", str(e))
        raise HTTPException(status_code=500, detail="Error getting tasks")

# Kill a task
@app.get("/kill_task/")
def kill_task(id: int):
    try:
        with SessionsLocal() as db:
            task = db.query(Tasks).filter_by(id=id).first()

            if task.state == "EXECUTING":
                process_id = task.process_id
                publish_to_mqtt("kill_task", {"task_id": id, "process_id": process_id})


    except Exception as e:
        logger.exception("Error killing task: %s", str(e))
        raise HTTPException(status_code=500, detail="Error killing task")

# Update task status
@app.put("/ci_task")
def put_data(body: dict):
    try:
        with SessionsLocal() as db:
            task_id = body["task_id"]

            task = db.query(Tasks).filter_by(id=task_id).first()
            task.process_id = None
            if int(body["exit_code"]) == 0:
                task.state = "PASSED"
            else:
                task.state = "FAILED"

            machine_id = task.state_machine_id
            machine = db.query(StateMachine).filter_by(id=machine_id).first()
            machine.state = 'FREE'
            task.state_machine_id = None

            db.commit()

        # Call new tasks to process.
        task_handler()

        return body


    except Exception as e:
        logger.exception("Error updating task status: %s", str(e))
        raise HTTPException(status_code=500, detail="Error updating task status")

# Update process ID for a task
@app.put("/ci_update_process_id")
def update_process_id(data: dict):
    try:
        with SessionsLocal() as db:
            task_id = data["task_id"]
            process_id = data["process_id"]

            task = db.query(Tasks).filter_by(id=task_id).first()
            task.process_id = process_id

            db.commit()

        return data

    except Exception as e:
        logger.exception("Error updating process ID: %s", str(e))
        raise HTTPException(status_code=500, detail="Error updating process ID")

# Mark a task as killed
@app.put("/kill_task_ok")
def kill_task(data: dict):

    # The kills.sh script never dies, its its sbuprocesses that are killed
    # that means that the bsf4.sh still sends a FAILED signal to the API and
    # shuts down the current execution.
    try:

        with SessionsLocal() as db:

            task_id = data["task_id"]
            task = db.query(Tasks).filter_by(id=task_id).first()
            task.state = "KILLED"
            # task.process_id = None

            # machine_id = task.state_machine_id
            # print(f"MACHINE ID CRL:  {machine_id}")
            # machine = db.query(StateMachine).filter_by(id=machine_id).first()
            # machine.state = "FREE"

            db.commit()

    except Exception as e:
        logger.exception("Error marking task as killed: %s", str(e))
        raise HTTPException(status_code=500, detail="Error marking task as killed")

# Update one task and state machine status
@app.get("/ci_task/")
def get_data(id: int):
    try:

        body = {}
        with SessionsLocal() as db:

            task = db.query(Tasks).filter_by(id=id).first()
            machine_id = task.state_machine_id
            machine = db.query(StateMachine).filter_by(id=machine_id).first()

            machine.state = 'EXECUTING'
            task.state = 'EXECUTING'
            task_id = task.id
            task_name = task.repository_name
            body = { "task_id": task_id, "task_name": task_name }
            db.commit()

        return body

    except Exception as e:
        logger.exception("Error updating task and machine status: %s", str(e))
        raise HTTPException(status_code=500, detail="Error updating task and machine status")

# Get all machines
@app.get("/machines")
def read_machines(skip: int = 0, limit: int = 10):
    try:
        with SessionsLocal() as db:
            data = db.query(StateMachine).offset(skip).limit(limit).all()

        return data

    except Exception as e:
        logger.exception("Error getting machines: %s", str(e))
        raise HTTPException(status_code=500, detail="Error getting machines")

# Hello World
@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
