import requests
import os

BASE_URL="http://127.0.0.1:8000"

directory_name = "~/.config/bsf"
file_path = os.path.join(directory_name, "authen")

def write(token):
  if not os.path.exists(directory_name):
    os.makedirs(directory_name)
  with open(file_path, "w") as file:
    file.write(token)
  print(f"Saving token in {file_path}")

def set_(token_):
  write(token_)

def get():
  with open(file_path, "r") as file:
    content = file.read()
  return ({"Content-Type":"application/json", "Authorization": f"Bearer {content}"})

def register():
  print("Username: ")
  username = input()
  print("Password: ")
  password = input()

  payload = { "username": username, "password": password }

  url = f"{BASE_URL}/register"
  response = requests.post(url, json=payload)
  response.raise_for_status()
  payload = response.json()

  print(payload)

def register_new():
  print("Username: ")
  username = input()
  print("Password: ")
  password = input()
  headers = get()
  #body = { "username": username, "password": password, "permissions": { "gcc": ["get", "kill"], "qemu": ["get"]}}
  payload = { "username": username, "password": password }

  url = f"{BASE_URL}/register"
  response = requests.post(url, json=payload, headers=headers)
  response.raise_for_status()
  payload = response.json()
  print(payload)

def change_user_permissions():
  print("Username: ")
  username = input()
  print("Permissions: (e.i GCC:GET:KILL-QEMU:GET")
  permissions = input()

  headers = get()
  payload = { "username": username, "permissions": permissions }

  url = f"{BASE_URL}/change_permissions"
  response = requests.put(url, json=payload, headers=headers)
  response.raise_for_status()
  payload = response.json()
  print(payload)


def login():
  print("Username: ")
  username = input()
  print("Password: ")
  password = input()

  payload = { "username": username, "password": password }

  url = f"{BASE_URL}/login"
  response = requests.post(url, json=payload)
  response.raise_for_status()
  payload = response.json()

  token = payload["token"]
  print(token)
  set_(token)

  print(payload)

def kill_task():
  print("Task id: ")
  task_id = input()

  payload = {"task_id": task_id}
  headers = get()

  url = f"{BASE_URL}/kill_task/"
  response = requests.get(url, json=payload, headers=headers)
  response.raise_for_status()
  payload = response.json()
  print(payload)

def protected():
  headers = get()
  print(headers)

  payload = { "username": "luis", "password": "password" }

  url = f"{BASE_URL}/protected"
  response = requests.get(url, json=payload, headers=headers)
  response.raise_for_status()
  payload = response.json()
  print(payload)

def unprotected():
  url = f"{BASE_URL}/unprotected"
  response = requests.get(url)
  response.raise_for_status()
  body = response.json()
  print(body)

if __name__ == "__main__":
  while True:
    print("1-Register, 2-Login, 3-kill task, 4-Unprotected, 5-Unprotected")
    print("6-Change Permissions")
    user_input = input()
    if user_input == "1":
      register_new()
    elif user_input == "2":
      login()
    elif user_input == "3":
      kill_task()
    elif user_input == "4":
      unprotected()
    elif user_input == "5":
      protected()
    elif user_input == "6":
      change_user_permissions()
