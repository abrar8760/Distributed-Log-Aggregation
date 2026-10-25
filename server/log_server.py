import socket
import threading
import queue
import time
from datetime import datetime
from pathlib import Path

HOST = "0.0.0.0"
PORT = 9999

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILES = {
    "INFO": "info.log",
    "WARNING": "warning.log",
    "ERROR": "error.log",
    "CRITICAL": "critical.log",
}

# Lower number means higher priority
PRIORITY = {
    "CRITICAL": 1,
    "ERROR": 2,
    "WARNING": 3,
    "INFO": 4,
}

log_queue = queue.PriorityQueue()
sequence_number = 0
sequence_lock = threading.Lock()

BATCH_WINDOW = 0.5


def process_log(item):
    priority, sequence, message, address, timestamp = item

    level, separator, content = message.partition(":")
    level = level.strip().upper()

    log_entry = f"[{timestamp}] {address[0]}: {message}"
    print(f"[PRIORITY {priority}] {log_entry}", flush=True)

    if separator and level in LOG_FILES:
        with open(LOG_DIR / LOG_FILES[level], "a", encoding="utf-8") as file:
            file.write(log_entry + "\n")

        with open(LOG_DIR / "received.log", "a", encoding="utf-8") as file:
            file.write(log_entry + "\n")
    else:
        print("Unrecognized log format; not saved.", flush=True)


def worker():
    while True:
        first_item = log_queue.get()
        batch = [first_item]

        # Collect messages that arrive within the short batching window
        deadline = time.monotonic() + BATCH_WINDOW

        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break

            try:
                batch.append(log_queue.get(timeout=remaining))
            except queue.Empty:
                break

        # PriorityQueue sorts by priority, then sequence number
        batch.sort(key=lambda item: (item[0], item[1]))

        for item in batch:
            try:
                process_log(item)
            except OSError as error:
                print(f"Could not save log: {error}", flush=True)
            finally:
                log_queue.task_done()


server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((HOST, PORT))

threading.Thread(target=worker, daemon=True).start()

print(f"Priority-based UDP Log Server listening on port {PORT}...")
print("Priority order: CRITICAL > ERROR > WARNING > INFO")

try:
    while True:
        data, address = server.recvfrom(4096)
        message = data.decode("utf-8", errors="replace").strip()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        level = message.partition(":")[0].strip().upper()
        priority = PRIORITY.get(level, 5)

        with sequence_lock:
            sequence_number += 1
            sequence = sequence_number

        log_queue.put((priority, sequence, message, address, timestamp))

except KeyboardInterrupt:
    print("\nUDP Log Server stopped.")

finally:
    server.close()
