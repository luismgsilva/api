import paho.mqtt.client as mqtt
from fastapi import FastAPI, HTTPException, Depends
import json
from datetime import datetime
import logging
from auth.auth import AuthHandler
from auth.schemas import AuthDetails
from auth.permissions import BitMapManager

from infra.repository.tasks_repository import TasksRepository
from infra.repository.machines_repository import MachinesRepository
from infra.repository.users_repository import UsersRepository

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
auth_handler = AuthHandler()

# Restructure
map1 = ["get", "start", "restart", "kill"]
map2 = { "gcc": 0*len(map1), "qemu": 1*len(map1) }
permission_handler = BitMapManager(map1, map2)

tasks_repo = TasksRepository()
machines_repo = MachinesRepository()
users_repo = UsersRepository()

# Publishes a message to an MQTT broker
def publish_to_mqtt(topic, **body):
    mqtt_broker = "localhost"
    mqtt_port = 1883
    mqtt_client = mqtt.Client()
    print(body)
    json_body = json.dumps(body)

    try:
        mqtt_client.connect(mqtt_broker, mqtt_port)
        mqtt_client.publish(topic, json_body)
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
        task_id = tasks_repo.select_test("state", "QUEUE", "id")
        machine_id = machines_repo.select_test("state", "AVAILABLE", "id")
        if task_id and machine_id:
            tasks_repo.update("id", task_id, state="PENDING")
            tasks_repo.update("id", task_id, machine_id=machine_id)
            machines_repo.update("id", machine_id, state="PENDING")
            publish_to_mqtt("start_task",  task_id=task_id )

    except Exception as e:
        logger.exception("Error processing task_handler")
        raise HTTPException(status_code=500, detail="Error processing task_handler")

# Process webhook payload
@app.post("/webhook")
def webhook_handler(payload: dict):
    try:
        repository_name = payload["repository"]["name"]
        pusher_name     = payload["pusher"]["name"]
        ref             = payload["ref"]
        after           = payload["after"]
        before          = payload["before"]

        if not has_permission(pusher_name, repository_name, "start"):
            raise HTTPException(status_code=401, detail="Permission denied")

        tasks_repo.insert(
            repository_name=repository_name,
            pusher_name=pusher_name,
            ref=ref,
            after=after,
            before=before
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
def read_data():
    try:
        tasks = tasks_repo.select()
        return tasks

    except Exception as e:
        logger.exception("Error getting tasks: %s", str(e))
        raise HTTPException(status_code=500, detail="Error getting tasks")

# Kill a task
@app.put("/kill_task")
def kill_task(body: dict, username=Depends(auth_handler.auth_wrapper)):
    try:
        if not users_repo.select_test("name", username, "is_superuser"):
            repository_name = tasks_repo.select_test("id", task_id, "repository_name")
            pusher_name = tasks_repo.select_test("id", task_id, "pusher_name")
            if not has_permission(username, repository_name, "kill"):
                raise HTTPException(status_code=401, detail="Permission denied")
            if not pusher_name == username:
                raise HTTPException(status_code=401, detail="Permission denied")

        task_id = body["task_id"]
        task_state = tasks_repo.select_test("id", task_id, "state")
        task_process_id = tasks_repo.select_test("id", task_id, "process_id")
        if task_state == "EXECUTING":
            publish_to_mqtt("kill_task", task_id=task_id, process_id=task_process_id)

    except Exception as e:
        logger.exception("Error killing task: %s", str(e))
        raise HTTPException(status_code=500, detail="Error killing task")

# Update task status
@app.put("/ci_task")
def put_data(body: dict):
    try:

        task_id = body["task_id"]
        tasks_repo.update("id", task_id, process_id=None)
        if int(body["exit_code"]) == 0:
            tasks_repo.update("id", task_id, state="PASSED")
        else:
            tasks_repo.update("id", task_id, state="FAILED")

        machine_id = tasks_repo.select_test("id", task_id, "machine_id")
        machines_repo.update("id", machine_id, state="AVAILABLE")
        tasks_repo.update("id", task_id, machine_id=None)

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
        tasks_repo.update("id", task_id, process_id=process_id)

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
        tasks_repo.update("id", task_id, state="KILLED")

    except Exception as e:
        logger.exception("Error marking task as killed: %s", str(e))
        raise HTTPException(status_code=500, detail="Error marking task as killed")

# Update one task and state machine status
@app.get("/ci_task/")
def get_data(id: int):
    try:
        machine_id = tasks_repo.select_test("id", id, "machine_id")
        machines_repo.update("id", machine_id, state="RUNNING")
        tasks_repo.update("id", id, state="EXECUTING")

        task_name = tasks_repo.select_test("id", id, "repository_name")
        ref = tasks_repo.select_test("id", id, "ref")
        before = tasks_repo.select_test("id", id, "before")
        after = tasks_repo.select_test("id", id, "after")
        
        body = {"task_id": id, "task_name": task_name, "ref": ref, "before": before, "after": after}

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
        user_id = users_repo.select_test("name", auth_details.username, "id")
        user_password = users_repo.select_test("name", auth_details.username, "password")

        if (user_id is None) or (not auth_handler.verify_password(auth_details.password, user_password)):
            raise HTTPException(status_code=500, detail="Invalid username and/or password")
        token = auth_handler.encode_token(auth_details.username)
        return { "token": token }

    except Exception as e:
        logger.exception("Error login: %s", str(e))
        raise HTTPException(status_code=500, detail="Error login")

# def register(auth_details: AuthDetails):
@app.post("/register")
#def register(body: dict, username=Depends(auth_handler.auth_wrapper)):
def register(payload: dict):
    try:
        if not has_permission(username):
            raise HTTPException(status_code=401, detail="Permission denied")

        name = payload["username"]
        if user_id:
            raise HTTPException(status_code=400, detail="Username is taken")

        hashed_password = auth_handler.get_password_hash(payload["password"])

        #permissions = body["permissions"]
        user_permissions = permission_handler.get_bit_map()
        #for key, value in permissions.items():
        #    user_permissions = permission_handler.add_permission(user_permissions, key, value)
        users_repo.insert(name=name, password=hashed_password, permissions=user_permissions)

    except Exception as e:
        logger.exception("Error register: %s", str(e))
        raise HTTPException(status_code=500, detail="Error register")

@app.put("/change_permissions")
def change_permissions(payload: dict, username=Depends(auth_handler.auth_wrapper)):
    try:
        if not has_permission(username):
            raise HTTPException(status_code=401, detail="Permission denied")

        username = payload["username"]
        permissions = payload["permissions"]
        
        # TODO: Validate permissions.
    
        user_permissions = users_repo.select_test("name", username, "permissions")
        user_permissions = permission_handler.add_permission(user_permissions, permissions)
        print("PERMISSIONS")       
        print(user_permissions) 
        users_repo.update("name", username, permissions=user_permissions)
    
    except Exception as e:
        logger.exception("Error change permission: %s", str(e))
        raise HTTPException(status_code=500, detail="Error register")

@app.get("/unprotected")
def unprotected():
  return { "hello": "world" }

def has_permission(username, module_name=None, permission_name=None):
    try:
        if module_name == None and permission_name == None:
            return users_repo.select_test("name", username, "is_superuser")

        user_permissions = users_repo.select_test("name", username, "permissions")
        return permission_handler.check_bit_map(user_permissions, module=module_name, permission=permission_name)

    except Exception as e:
        logger.exception("Error login: %s", str(e))
        raise HTTPException(status_code=500, detail="Error login")

@app.get("/protected")
def protected(body: dict, username=Depends(auth_handler.auth_wrapper)):
    if not has_permission(username, "gcc", "start"):
        raise HTTPException(status_code=401, detail="Permission denied")

    return { "name": username }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
