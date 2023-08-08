import paho.mqtt.client as mqtt

# Callback function when the client connects to the MQTT broker
def on_connect(client, userdata, flags, rc):
  print("Connected to MQTT broker with result code " + str(rc))
  client.subscribe("webhook_data")

# Callback function when a message is received on the subscrived topic
def on_message(client, userdata, msg):
  print("received message on topic: ", msg.topic)
  print("Message payload:", msg.payload.decode("utf-8"))

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