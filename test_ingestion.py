import requests
import uuid

url = "http://localhost:8000/api/v1/telemetry"
payload = {"vehicle_id": str(uuid.uuid4()), "driver_id": str(uuid.uuid4()), "data": []}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
