import paho.mqtt.client as mqtt
import subprocess
import requests
import json
import logging
import time

# Constants
BASE_URL          = "http://127.0.0.1:8000"
START_TASK_SCRIPT = "/home/luis/work/thesis/api/scripts/bsf4.sh"
KILL_TASK_SCRIPT  = "/home/luis/work/thesis/api/scripts/kills.sh"

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to start a task
def start_task(body: dict):

    print("Ola")

    time.sleep(1)

    try:
        task_id = str(body["task_id"])

        # Request task to execute
        url = f"{BASE_URL}/ci_task/?id={task_id}"
        response = requests.get(url)
        response.raise_for_status()
        body = response.json()
        print(body)

        task_name = str(body["task_name"])

        # Start the subprocess and get its PID
        # process = subprocess.Popen(f"bash {START_TASK_SCRIPT} {task_id}", shell=True)
        process = subprocess.Popen(["bash", START_TASK_SCRIPT, task_name, task_id])
        logger.info(f"Started task with PID: {process.pid}")

        # Update task database with the associated process PID
        url = f"{BASE_URL}/ci_update_process_id"
        body["process_id"] = process.pid
        response = requests.put(url, json=body)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        logger.error("Error while starting task:", exc_info=True)

# Function to kill a task
def kill_task(body: dict):
    try:
        process_id = str(body["process_id"])
        task_id = str(body["task_id"]) # Unused

        # subprocess.run(f"bash {KILL_TASK_SCRIPT} {process_id}", shell=True)
        subprocess.run(["bash", KILL_TASK_SCRIPT, process_id])
        logger.info(f"Killed process: {process_id}")

        url = f"{BASE_URL}/kill_task_ok"
        response = requests.put(url, json=body)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        logger.error("Error while killing task:", exc_info=True)

# Callback function when the client connects to the MQTT broker
def on_connect(client, userdata, flags, rc):
    logger.info("Connected to MQTT broker with result code " + str(rc))
    client.subscribe("start_task")
    client.subscribe("kill_task")

# Callback function when a message is received on the subscribed topic
def on_message(client, userdata, msg):
    try:
        logger.info("Received message on topic: %s", msg.topic)
        body = msg.payload.decode("utf-8")
        body = json.loads(body)
        logger.info("Message payload: %s", body)

        if msg.topic == "start_task":
            start_task(body)
        elif msg.topic == "kill_task":
            kill_task(body)

    except json.JSONDecodeError as e:
        logger.error("Error decoding JSON:", exc_info=True)
    except Exception as e:
        logger.error("Error processing message:", exc_info=True)

# Create an MQTT client instance
mqtt_client = mqtt.Client()

# Set the callback functions
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Connect to the MQTT broker
mqtt_broker = "localhost"
mqtt_port = 1883
mqtt_client.connect(mqtt_broker, mqtt_port, 60)

# Start the MQTT client loop to listen for messages
mqtt_client.loop_forever()
