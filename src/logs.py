import os
from datetime import datetime

LOGS_PATH = "logs"
os.makedirs(LOGS_PATH, exist_ok=True)

def log_prompt(user_id: int, prompt: str):
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = os.path.join(LOGS_PATH, f"{user_id}.log")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{time}] {prompt}\n")
