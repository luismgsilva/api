
**General Setup**
```bash
$ python3 -m venv myenv
$ source myenv/bin/activate
$ pip install fastapi Version: 0.101.0
$ pip install uvicorn Version: 0.23.2
$ pip install sqlalchemy Version: 2.0.19
$ pip install paho-mqtt Version: 1.6.1
$ pip install requests Version: 2.31.0
$ pip install PyJWT Version: 2.8.0
$ pip install passlib Version: 1.7.4
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
$ python3 api.py
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