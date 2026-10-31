import socket
import sys
import uuid
import time

SERVER_IP = "10.0.0.3"
SERVER_PORT = 9999

ACK_TIMEOUT = 1.0

if len(sys.argv) < 3:
    print('Usage: python3 client/log_client.py LEVEL "message"')
    sys.exit(1)

level = sys.argv[1].upper()
message = " ".join(sys.argv[2:])

valid_levels = {"INFO", "WARNING", "ERROR", "CRITICAL"}

if level not in valid_levels:
    print("Invalid level. Use INFO, WARNING, ERROR, or CRITICAL.")
    sys.exit(1)

# Generate a unique packet ID
packet_id = str(uuid.uuid4())

# Prepare packet
packet = f"DATA|{packet_id}|{level}|{message}"

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.settimeout(ACK_TIMEOUT)

sent = 1
received = 0

try:
    start_time = time.monotonic()

    # Send UDP packet
    client.sendto(
        packet.encode("utf-8"),
        (SERVER_IP, SERVER_PORT)
    )

    print(f"Sent log to {SERVER_IP}:{SERVER_PORT}: {level}: {message}")
    print(f"Packet ID: {packet_id}")

    try:
        # Wait for server acknowledgement
        data, address = client.recvfrom(4096)
        acknowledgement = data.decode("utf-8", errors="replace").strip()

        if acknowledgement == f"ACK|{packet_id}":
            received = 1
            print("Server acknowledgement received.")
        else:
            print("Invalid acknowledgement received.")

    except socket.timeout:
        print("Acknowledgement not received within timeout.")

    elapsed = time.monotonic() - start_time

    lost = sent - received
    delivery_rate = (received / sent) * 100
    packet_loss = (lost / sent) * 100

    print("\n--- PACKET DELIVERY REPORT ---")
    print(f"Packets sent: {sent}")
    print(f"Packets acknowledged: {received}")
    print(f"Unacknowledged packets: {lost}")
    print(f"Delivery rate: {delivery_rate:.2f}%")
    print(f"Unacknowledged rate: {packet_loss:.2f}%")
    print(f"Measurement time: {elapsed:.3f} seconds")

finally:
    client.close()
