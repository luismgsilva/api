import requests
import json

def load_json_from_file(filename):
    try:
        with open(filename, "r") as file:
            data_dict = json.load(file)
            return data_dict
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in '{filename}': {e}")


def send_post_request(url, data):
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # Check if the request was successful
        print("HTTP POST request sent successfully!")
        print("Response status code:", response.status_code)
        print("Response body:", response.text)
    except requests.exceptions.RequestException as e:
        print("Error sending HTTP POST request:", e)

# Example usage
if __name__ == "__main__":
    url = "http://127.0.0.1:8000/webhook"

    # Load JSON data from the file and convert to a dictionary
    data = load_json_from_file("webhook.json")

    send_post_request(url, data)
