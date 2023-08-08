
**General Setup**
```bash
$ python3 -m venv myenv 
$ source myenv/bin/activate 
$ pip install fastapi uvicorn 
$ pip install sqlalchemy
$ pip install paho-mqtt
```


**MQTT mosquitto setup**
```bash
# Install Mosquitoo
$ sudo apt-get install mosquitto mosquitto-clients

# Start and Enable Mosquitto
$ sudo systemctl start mosquitto
$ sudo systemctl enable mosquitto

# Test the Instalation
$ mosquito_sub -h localhost -t test/topic
$ mosquito_pub -h localhost -t test/topic -m "Hello World!"

# Configure Access Control to enable 
# password-based Authentication
$ sudo mosquitto_passwd -c /etc/mosquitto/passwd <username>
$ sudo cat /etc/mosquitto/mosquitto.conf << 'EOF'
allow_anonymous false
password_file /etc/mosquitto/passwd
EOF
$ sudo systemctl restart mosquitto
```

**Create BD**
```bash
$ python3 bd.py
```

**Initialize API**
```bash
$ uvicorn api:app --reload
```

**Initialize MQTT Subscriber**
```bash
$ python3 sub.py
```

**Proxy**

```bash
# https://ngrok.com/download
$ ngrok http 8000
```