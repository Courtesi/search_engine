import json

def store(index: dict):
    with open("stored_index.json", "w") as f:
        json.dump(index, f)