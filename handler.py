import sys
import requests
import json
import time

def main(task_id):
    base_url = "https://f63c-213-22-250-155.ngrok.io/task"

    url = f"{base_url}/?id={task_id}"

    try:
        time.sleep(10)

        response = requests.get(url)
        # Raise an exception for HTTP errors
        response.raise_for_status()

        json_response = response.json()

        # Save the JSON response to a file
        with open("task_response.json", "w") as file:
            json.dump(json_response, file, indent=4)

        time.sleep(10)

        print("JSON response saved successfully.")

        data = { "state": "PASSED" }

        response = requests.put(url, json=data)
        response.raise_for_status()


    except requests.exceptions.RequestException as e:
        print("Error:", e)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <task_id>")
        sys.exit(1)

    task_id = int(sys.argv[1])
    main(task_id)
