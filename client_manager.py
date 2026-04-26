# client_manager.py
# Handles saving and loading client profiles as JSON files
# Each client stored as clients/firstname_lastname.json

import json
import os

CLIENTS_DIR = "clients"

def ensure_clients_dir():
    # Creates the clients folder if it doesn't exist yet
    if not os.path.exists(CLIENTS_DIR):
        os.makedirs(CLIENTS_DIR)

def get_saved_clients():
    # Returns list of saved client names for the dropdown
    ensure_clients_dir()
    files = [f for f in os.listdir(CLIENTS_DIR) if f.endswith(".json")]
    names = [f.replace(".json", "").replace("_", " ").title() for f in files]
    return sorted(names)

def name_to_filename(client_name):
    # Converts "David Chen" → "clients/david_chen.json"
    import re
    safe_name = re.sub(r'[^\w\s-]', '', client_name.strip().lower())
    safe_name = re.sub(r'[\s]+', '_', safe_name)
    safe_name = safe_name.strip('_')
    return os.path.join(CLIENTS_DIR, f"{safe_name}.json")

def save_client(client_name, data):
    # Saves all sidebar inputs to a JSON file
    ensure_clients_dir()
    filepath = name_to_filename(client_name)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    return filepath

def load_client(client_name):
    # Loads a client's saved inputs from their JSON file
    filepath = name_to_filename(client_name)
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r") as f:
        return json.load(f)

def delete_client(client_name):
    # Permanently deletes a client's JSON file
    filepath = name_to_filename(client_name)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False