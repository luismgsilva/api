import paho.mqtt.client as mqtt
from fastapi import FastAPI, HTTPException, Depends
# from sqlalchemy import create_engine, Column, Integer, String, Sequence
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from bd import StateMachine, Tasks, User
# from pydantic import BaseModel
import json
from datetime import datetime
import logging
from auth.auth import AuthHandler
from auth.schemas import AuthDetails

from infra.repository.tasks_repository import TasksRepository
from infra.repository.machines_repository import MachinesRepository
from infra.repository.users_repository import UsersRepository

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
auth_handler = AuthHandler()

tasks_repo = TasksRepository()
machines_repo = MachinesRepository()
users_repo = UsersRepository()

# Publishes a message to an MQTT broker
def publish_to_mqtt(topic, **body):
    mqtt_broker = "localhost"
    mqtt_port = 1883
    mqtt_client = mqtt.Client()
    body = json.dumps(body)

    try:
        mqtt_client.connect(mqtt_broker, mqtt_port)
        mqtt_client.publish(topic, body)
        mqtt_client.disconnect()
    except Exception as e:
        logger.error("Error publishing to MQTT: %s", str(e))

# Write payload to a file for debug purposes
def debug(payload: dict):
    file_path = "webhook.json"
    with open(file_path, 'w') as json_file:
        json.dump(payload, json_file, indent=4)

def task_handler():

    try:

        task = tasks_repo.search_by_state(state="QUEUE")
        machine = machines_repo.search_by_state(state="AVAILABLE")
        print(f"TASK: {task}")
        print(f"MACHINE: {machine}")
        if task and machine:
            tasks_repo.update(task.id, state="PENDING")
            tasks_repo.update(task.id, machine_id=machine.id)
            machines_repo.update(machine.id, state="PENDING")
            publish_to_mqtt("start_task",  task_id=task.id )

    except Exception as e:
        logger.exception("Error processing task_handler")
        raise HTTPException(status_code=500, detail="Error processing task_handler")

# Process webhook payload
@app.post("/webhook")
# def webhook_handler(payload: WebhookPayload):
def webhook_handler(payload: dict):
    try:

        tasks_repo = TasksRepository()
        tasks_repo.insert(
            repository_name=payload["repository"]["name"],
            pusher_name=payload["pusher"]["name"]
        )
         # Write payload to file for debug purposes
        debug(payload)
        task_handler()

        return payload

    except Exception as e:
        logger.exception("Error processing webhook: %s", str(e))
        raise HTTPException(status_code=500, detail="Error processing webhook")

# Get all tasks
@app.get("/tasks")
def read_data(skip: int = 0, limit: int = 10):
    try:

        tasks = tasks_repo.select()
        return tasks

    except Exception as e:
        logger.exception("Error getting tasks: %s", str(e))
        raise HTTPException(status_code=500, detail="Error getting tasks")

# Kill a task
@app.get("/kill_task/")
def kill_task(id: int):
    try:

        task = tasks_repo.search_by_id(id=id)
        if task.state == "EXECUTING":
            process_id = task.process_id
            publish_to_mqtt("kill_task", task_id=id, process_id=process_id)

    except Exception as e:
        logger.exception("Error killing task: %s", str(e))
        raise HTTPException(status_code=500, detail="Error killing task")

# Update task status
@app.put("/ci_task")
def put_data(body: dict):
    try:

        task_id = body["task_id"]
        tasks_repo.update(task_id, process_id=None)
        if int(body["exit_code"]) == 0:
            tasks_repo.update(task_id, state="PASSED")
        else:
            tasks_repo.update(task_id, state="FAILED")

        machine_id = tasks_repo.get_data(task_id, "machine_id")
        machines_repo.update(machine_id, state="AVAILABLE")
        tasks_repo.update(task_id, machine_id=None)

        # Call new tasks to process.
        task_handler()

        return body


    except Exception as e:
        logger.exception("Error updating task status: %s", str(e))
        raise HTTPException(status_code=500, detail="Error updating task status")

# Update process ID for a task
@app.put("/ci_update_process_id")
def update_process_id(body: dict):
    try:

        task_id = body["task_id"]
        process_id = body["process_id"]
        tasks_repo.update(task_id, process_id=process_id)

        return body

    except Exception as e:
        logger.exception("Error updating process ID: %s", str(e))
        raise HTTPException(status_code=500, detail="Error updating process ID")


# This is being executed before the /ci_task which changes the state from "KILLED" to "FAILED"
# Mark a task as killed
@app.put("/kill_task_ok")
def kill_task(data: dict):

    # The kills.sh script never dies, its its sbuprocesses that are killed
    # that means that the bsf4.sh still sends a FAILED signal to the API and
    # shuts down the current execution.
    try:
        task_id = data["task_id"]
        print(f"LUIS TASK ID: {task_id}")
        tasks_repo.update(task_id, state="KILLED")

    except Exception as e:
        logger.exception("Error marking task as killed: %s", str(e))
        raise HTTPException(status_code=500, detail="Error marking task as killed")

# Update one task and state machine status
@app.get("/ci_task/")
def get_data(id: int):
    try:
        machine_id = tasks_repo.get_data(id, "machine_id")
        machines_repo.update(machine_id, state="RUNNING")
        tasks_repo.update(id, state="EXECUTING")

        task_name = tasks_repo.get_data(id, "repository_name")
        body = {"task_id": id, "task_name": task_name}

        return body


    except Exception as e:
        logger.exception("Error updating task and machine status: %s", str(e))
        raise HTTPException(status_code=500, detail="Error updating task and machine status")

# Get all machines
@app.get("/machines")
def read_machines(skip: int = 0, limit: int = 10):
    try:
        return machines_repo.select()

    except Exception as e:
        logger.exception("Error getting machines: %s", str(e))
        raise HTTPException(status_code=500, detail="Error getting machines")


@app.post("/login")
def login(auth_details: AuthDetails):
    try:
        user = users_repo.select_by_name(auth_details.username)
        user_password = users_repo.search_by_name(auth_details.username, "password")

        if (user is None) or (not auth_handler.verify_password(auth_details.password, user_password)):
            raise HTTPException(status_code=500, detail="Invalid username and/or password")
        token = auth_handler.encode_token(auth_details.username)
        return { "token": token }

    except Exception as e:
        logger.exception("Error login: %s", str(e))
        raise HTTPException(status_code=500, detail="Error login")

@app.post("/register")
def register(auth_details: AuthDetails):
    try:
        user = users_repo.select_by_name(auth_details.username)
        if user:
          raise HTTPException(status_code=400, detail="Username is taken")
        hashed_password = auth_handler.get_password_hash(auth_details.password)
        users_repo.insert(
            name=auth_details.username,
            password = hashed_password,
            permission = "common"
        )
    except Exception as e:
        logger.exception("Error register: %s", str(e))
        raise HTTPException(status_code=500, detail="Error register")

@app.get("/unprotected")
def unprotected():
  return { "hello": "world" }

# @app.get("/protected", dependencies=[Depends(has_permission, required_permission="can_access_protected")])
# @app.get("/protected", dependencies=[Depends(auth_handler.auth_wrapper), Depends(has_permission, required_permission="can_access_protected")])
# @app.get("/protected", dependencies=[Depends(auth_handler.auth_wrapper)])

def has_permission(username, required_permission=None):
    try:
        if required_permission == None:
            return True

        user_permission = users_repo.search_by_name(username, "permission")
        if user_permission == required_permission:
            return True

        return False
    except Exception as e:
        logger.exception("Error login: %s", str(e))
        raise HTTPException(status_code=500, detail="Error login")

@app.get("/protected")
def protected(body: dict, username=Depends(auth_handler.auth_wrapper)):
    if not has_permission(username, "common"):
        raise HTTPException(status_code=401, detail="Permission denied")
    return { "name": username }

# Hello World
@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
