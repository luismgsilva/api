
**Setup**
```bash
$ python3 -m venv myenv 
$ source myenv/bin/activate 
$ pip install fastapi uvicorn 
$ pip install sqlalchemy
```

**Create BD**
```bash
$ python3 bd.py
```

**Initialize API**
```bash
$ uvicorn api:app --reload
```

**Proxy**

```bash
# https://ngrok.com/download
$ ngrok http 8000
```