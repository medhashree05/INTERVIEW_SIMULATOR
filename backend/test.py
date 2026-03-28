import json
with open("firebase_key.json") as f:
    data = json.load(f)
print(json.dumps(data))   # prints it as a valid single-line JSON string