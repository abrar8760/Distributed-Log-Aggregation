import socket
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

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((HOST, PORT))

print(f"UDP Log Server listening on port {PORT}...")

try:
    while True:
        data, address = server.recvfrom(4096)
        message = data.decode("utf-8", errors="replace").strip()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {address[0]}: {message}"

        print(log_entry, flush=True)

        level, separator, content = message.partition(":")
        level = level.strip().upper()

        if separator and level in LOG_FILES:
            filename = LOG_FILES[level]
            with open(LOG_DIR / filename, "a", encoding="utf-8") as file:
                file.write(log_entry + "\n")
        else:
            print("Unrecognized log format; not saved to a severity file.")

except KeyboardInterrupt:
    print("\nUDP Log Server stopped.")

finally:
    server.close()

