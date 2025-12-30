import time
import random
import requests

BASE = "http://127.0.0.1:8000"

def post_data(device_id: str, value):
    r = requests.post(f"{BASE}/api/data", json={"device_id": device_id, "value": value}, timeout=5)
    r.raise_for_status()
    return r.json()

def send_control(target: str, command: str, args=None):
    r = requests.post(
        f"{BASE}/api/control",
        json={"target": target, "command": command, "args": args or {}},
        timeout=5,
    )
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    for _ in range(5):
        v = {"rpm": random.randint(900, 1600), "mode": "auto"}
        out = post_data("device_two", v)
        print("[device_two] posted REST data:", out["event"])
        time.sleep(1)

    out = send_control("device_one", "set_threshold", {"min": 22.0, "max": 28.0})
    print("[device_two] sent control:", out["event"])

    status = requests.get(f"{BASE}/api/status", timeout=5).json()
    print("[device_two] status:", status)
