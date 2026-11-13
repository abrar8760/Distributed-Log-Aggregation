# Distributed Log Aggregation

A Computer Networks project that collects severity-labelled log messages from virtual network hosts, sends them over UDP, and stores them centrally. The project uses Python, Mininet, Open vSwitch (OVS), and OS-Ken.

## Project overview

The project demonstrates:

- Log clients running on Mininet hosts `h1` and `h2`.
- A central UDP log server running on `h3`.
- Log messages sent to `10.0.0.3` on UDP port `9999`.
- Classification and storage of `INFO`, `WARNING`, `ERROR`, and `CRITICAL` messages.
- Severity priority mapping: `CRITICAL = 1`, `ERROR = 2`, `WARNING = 3`, `INFO = 4`.
- Network connectivity and congestion experiments using Mininet.

The server stores messages in `logs/received.log` and the corresponding severity-specific files. The priority queue processes messages in short batches; priority ordering is therefore applied within a batch, not as a guarantee that every message across all time is globally reordered.

## Network topology

The custom Mininet topology contains:

| Host/device | Role | Address |
|---|---|---|
| `h1` | Log-generating client | `10.0.0.1` |
| `h2` | Additional client / background traffic generator | `10.0.0.2` |
| `h3` | Log server and iperf receiver | `10.0.0.3` |
| `s1`, `s2` | Open vSwitch switches | — |

The congestion topology uses a shaped inter-switch link configured as `bw=0.1`, which represents 0.1 Mbps (100 Kbps) when Mininet is started with `--link tc`.

## Requirements

The demonstrated environment uses:

- Ubuntu (tested in VirtualBox)
- Python 3
- Mininet
- Open vSwitch
- OS-Ken
- iperf2
- Git

The project directory used in the command examples is:

```bash
~/ditributed-log-aggregation
```

Use this exact spelling if that is the name of your local folder.

---

## Part A — Run the SDN log aggregation demonstration

Use this procedure for the OS-Ken/OpenFlow 1.3 demonstration. Open separate Ubuntu terminal windows for the controller and Mininet.

### 1. Start the OS-Ken controller — Ubuntu Terminal 1

```bash
source ~/ryu311-env/bin/activate
cd ~/ditributed-log-aggregation
osken-manager controller/log_controller.py
```

Keep this terminal open while using the SDN topology. The virtual environment is named `ryu311-env`, but the controller command used here is `osken-manager`.

### 2. Start the Mininet topology — Ubuntu Terminal 2

Run this only if a Mininet topology is not already running:

```bash
cd ~/ditributed-log-aggregation
sudo mn --custom topology/log_topology.py --topo logtopo --switch ovs,protocols=OpenFlow13 --controller=remote,ip=127.0.0.1,port=6653
```

At the `mininet>` prompt, check connectivity:

```text
pingall
```

The expected result for a healthy six-pair test is `0% dropped (6/6 received)`. Use the actual output from your run when reporting results.

### 3. Start the log server on h3

At the `mininet>` prompt:

```text
h3 python3 /home/mohammed_abrar_a/ditributed-log-aggregation/server/log_server.py > /tmp/priority_server.log 2>&1 &
```

Verify that the server process is running:

```text
h3 pgrep -af log_server.py
```

Verify that UDP port `9999` is listening:

```text
h3 sudo ss -lunp | grep 9999
```

View the server output:

```text
h3 cat /tmp/priority_server.log
```

An empty output file does not by itself mean the server has failed. Check the process and listening port as well.

### 4. Send log messages from h1 — normal Ubuntu Terminal 3

These commands are entered in a normal Ubuntu terminal, not at the `mininet>` prompt:

```bash
cd ~/ditributed-log-aggregation
sudo mnexec -a $(pgrep -f 'mininet:h1' | head -n 1) python3 ~/ditributed-log-aggregation/client/log_client.py INFO "Information test from h1"
sudo mnexec -a $(pgrep -f 'mininet:h1' | head -n 1) python3 ~/ditributed-log-aggregation/client/log_client.py WARNING "Warning test from h1"
sudo mnexec -a $(pgrep -f 'mininet:h1' | head -n 1) python3 ~/ditributed-log-aggregation/client/log_client.py ERROR "Error test from h1"
sudo mnexec -a $(pgrep -f 'mininet:h1' | head -n 1) python3 ~/ditributed-log-aggregation/client/log_client.py CRITICAL "Critical test from h1"
```

To send a message from h2:

```bash
sudo mnexec -a $(pgrep -f 'mininet:h2' | head -n 1) python3 ~/ditributed-log-aggregation/client/log_client.py INFO "Information test from h2"
```

### 5. Inspect the log files — Ubuntu terminal

```bash
cd ~/ditributed-log-aggregation
cat logs/received.log
cat logs/info.log
cat logs/warning.log
cat logs/error.log
cat logs/critical.log
```

`received.log` contains the aggregate received messages. Each severity-specific file contains messages classified at that severity.

### 6. Run the automated tests — Ubuntu terminal

```bash
cd ~/ditributed-log-aggregation
python3 tests/test_client.py
python3 tests/test_priority.py
```

The client tests check rejection of an invalid severity, rejection of a missing message, and acceptance of a valid severity. The priority test checks the configured severity-to-priority mapping. These tests do not, by themselves, prove successful network delivery or ACK reception.

---

## Part B — Run the congestion and delivery experiment

This is a separate Mininet run using traffic control (`tc`) to shape the inter-switch link. Stop the previous Mininet session before starting this topology. The congestion experiment can be run independently of the OS-Ken controller demonstration.

### 1. Clean up and start the congestion topology — Ubuntu terminal

```bash
sudo mn -c
cd ~/ditributed-log-aggregation
sudo mn --custom /home/mohammed_abrar_a/ditributed-log-aggregation/topology/log_topology.py --topo logtopo --switch ovsbr --link tc
```

At the `mininet>` prompt:

```text
pingall
```

### 2. Start the log server on h3

```text
h3 python3 /home/mohammed_abrar_a/ditributed-log-aggregation/server/log_server.py > /tmp/priority_server.log 2>&1 &
```

Verify it:

```text
h3 pgrep -af log_server.py
h3 sudo ss -lunp | grep 9999
```

### 3. Start the UDP iperf receiver on h3

```text
h3 iperf -s -u -p 5001 > /tmp/iperf_receiver.txt 2>&1 &
```

### 4. Generate background UDP traffic from h2

```text
h2 iperf -c 10.0.0.3 -u -p 5001 -b 2M -t 20 > /tmp/iperf_sender.txt 2>&1 &
```

This requests 2 Mbps of UDP traffic. The inter-switch link is configured for 100 Kbps, so the offered traffic exceeds the configured link capacity.

### 5. Run the delivery test from h1

Run while the background traffic is active:

```text
h1 python3 /home/mohammed_abrar_a/ditributed-log-aggregation/tests/test_delivery.py
```

The test sends 100 log packets and reports how many matching ACKs it receives within its configured timeout.

### 6. Stop background traffic and run the baseline

```text
h2 pkill iperf
h3 pkill iperf
```

Then run the same delivery test without the iperf background traffic:

```text
h1 python3 /home/mohammed_abrar_a/ditributed-log-aggregation/tests/test_delivery.py
```

### 7. Inspect the server-side evidence

```text
h3 pgrep -af log_server.py
h3 sudo ss -lunp | grep 9999
h3 cat /tmp/priority_server.log
```

The server log can help establish whether messages reached h3. For a clean experiment, clear or rotate the server log before each trial, then compare the number of unique test packet IDs received with the number of ACKs reported by h1.

---

## Understanding the delivery results

The delivery test's ACK count and the actual number of packets received by h3 are different measurements.

- **Packets sent**: number of log datagrams transmitted by the client.
- **Packets acknowledged**: number of matching ACK responses received by the client before the timeout.
- **Unacknowledged packets**: sent packets for which the client did not receive a matching ACK in time.
- **Delivery rate in this report**: ACK-based rate, not an independent count of packets received by h3.

Therefore, `0` acknowledgements does **not** by itself prove that all 100 original log packets were lost. The original packets may have reached h3 while the ACKs were missing, delayed, or not returned successfully. Compare the client report with a clean server-side count of unique packet IDs to distinguish these cases.

UDP does not automatically provide delivery acknowledgements. Any ACK in this project is application-level behaviour implemented by the client and server. An ACK should be interpreted according to the point at which the server sends it; an ACK sent after queue insertion does not necessarily prove that the log has been written to disk.

Congestion results can vary between trials. Do not assume that every congested run must produce packet loss or zero ACKs, and do not report a fixed result unless it was observed in that specific run. Record the actual output from each trial.

## Log severity and priority

| Severity | Priority | Meaning |
|---|---:|---|
| `CRITICAL` | 1 | Most urgent condition |
| `ERROR` | 2 | An operation failed |
| `WARNING` | 3 | A potential issue |
| `INFO` | 4 | Normal event or status |

A lower priority number represents a higher severity.

## Common troubleshooting checks

| Problem | Checks |
|---|---|
| `osken-manager` not found | Run `source ~/ryu311-env/bin/activate`, then `which osken-manager`. |
| Mininet is already running | Reuse the existing session or clean it up before starting a different topology. |
| `pingall` reports packet loss | Check topology startup, switch/controller connection, and controller port `6653` for Part A. |
| No server process appears | Run `h3 pgrep -af log_server.py` at the `mininet>` prompt. |
| UDP port 9999 is not listening | Start the server on h3 and check `h3 sudo ss -lunp \| grep 9999`. |
| Server receives no test message | Check that h3 is running the server, the destination is `10.0.0.3:9999`, and the client runs in the h1/h2 namespace. |
| Zero ACKs are reported | Check server receipt separately; zero ACKs do not prove that all original UDP packets were lost. |
| Priority order appears to be arrival order | Messages may have arrived outside the same short batching window. |

## Future improvements

- We used only two log clients (h1 and h2). In the future, we could add more clients to make the network bigger and increase project complexity.
- We could test the project with different numbers of clients and compare the results.
- We could improve the system to handle more log messages at the same time.
- We could make packet delivery and acknowledgement testing more accurate.
- We could improve the system to handle network congestion more effectively.
