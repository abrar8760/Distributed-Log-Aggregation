import socket
import sys

SERVER_IP = "10.0.0.3"
SERVER_PORT = 9999

if len(sys.argv) < 3:
    print('Usage: python3 client/log_client.py LEVEL "message"')
    sys.exit(1)

level = sys.argv[1].upper()
message = " ".join(sys.argv[2:])

valid_levels = {"INFO", "WARNING", "ERROR", "CRITICAL"}

if level not in valid_levels:
    print("Invalid level. Use INFO, WARNING, ERROR, or CRITICAL.")
    sys.exit(1)

log_message = f"{level}: {message}"

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    client.sendto(
        log_message.encode("utf-8"),
        (SERVER_IP, SERVER_PORT)
    )
    print(f"Sent log to {SERVER_IP}:{SERVER_PORT}: {log_message}")
finally:
    client.close()
