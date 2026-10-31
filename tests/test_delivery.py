import socket
import uuid
import time

SERVER_IP = "10.0.0.3"
SERVER_PORT = 9999

TOTAL_PACKETS = 100
ACK_TIMEOUT = 2.0

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.settimeout(0.1)

sent_ids = set()
acknowledged_ids = set()

start_time = time.monotonic()

# Send 100 uniquely numbered packets
for number in range(1, TOTAL_PACKETS + 1):
    packet_id = str(uuid.uuid4())
    sent_ids.add(packet_id)

    message = f"DATA|{packet_id}|INFO|Delivery test packet {number}"

    client.sendto(
        message.encode("utf-8"),
        (SERVER_IP, SERVER_PORT)
    )

# Collect acknowledgements
deadline = time.monotonic() + ACK_TIMEOUT

while time.monotonic() < deadline:
    try:
        data, address = client.recvfrom(4096)
        acknowledgement = data.decode("utf-8", errors="replace").strip()

        if acknowledgement.startswith("ACK|"):
            packet_id = acknowledgement.split("|", 1)[1]

            if packet_id in sent_ids:
                acknowledged_ids.add(packet_id)

    except socket.timeout:
        continue

elapsed = time.monotonic() - start_time

received = len(acknowledged_ids)
unacknowledged = TOTAL_PACKETS - received

delivery_rate = (received / TOTAL_PACKETS) * 100
unacknowledged_rate = (unacknowledged / TOTAL_PACKETS) * 100

print("\n========== DELIVERY REPORT ==========")
print(f"Packets sent: {TOTAL_PACKETS}")
print(f"Packets acknowledged: {received}")
print(f"Unacknowledged packets: {unacknowledged}")
print(f"Delivery rate: {delivery_rate:.2f}%")
print(f"Unacknowledged rate: {unacknowledged_rate:.2f}%")
print(f"Measurement time: {elapsed:.3f} seconds")
print("=====================================")

client.close()
