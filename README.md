# Distributed Log Aggregation

A Computer Networks project that collects log messages from network hosts using UDP, classifies them by severity, and stores them centrally. The lab environment uses Mininet and Open vSwitch to emulate a small network and OS-Ken as the SDN controller framework.

## Project overview

The system has three main parts:

1. **Log client** — sends a severity-labelled log message to the server over UDP. The updated client assigns a packet ID and waits for a matching acknowledgement (ACK).
2. **Log server** — receives log messages, places them in a priority queue, and writes them to severity-specific log files.
3. **Mininet topology** — emulates hosts and switches so delivery and congestion behaviour can be tested in a controlled network.

> The ACK in the current implementation confirms that the server accepted a message into its in-memory queue. It does not independently prove that the message was written to disk.

## Repository structure

```text
.
├── backups/       # Original copies of selected project files
├── client/        # UDP log client
├── controller/    # Controller-related project files
├── logs/          # Log output files (generated during tests)
├── results/       # Experimental results
├── screenshots/   # Evidence images from the Mininet experiments
├── server/        # UDP log server and priority queue
├── tests/         # Delivery and priority test scripts
├── topology/      # Custom Mininet topology
├── .gitignore
└── README.md
```

## Network topology

The current custom topology contains:

- `h1` — log-generating client (`10.0.0.1`)
- `h2` — background traffic generator (`10.0.0.2`)
- `h3` — log server and UDP iperf receiver (`10.0.0.3`)
- `s1` and `s2` — Open vSwitch bridges
- A shaped link between `s1` and `s2`

The topology file currently sets the inter-switch link to `bw=0.1`, which represents **0.1 Mbps (100 Kbps)** when launched with Mininet's `tc` link support.

## Requirements

The lab environment used Ubuntu in VirtualBox with:

- Python 3
- Mininet
- Open vSwitch
- iperf (iperf2 syntax)
- Git

OS-Ken is part of the broader SDN project environment. The current log-client/server delivery experiment can be run independently of starting an SDN controller, unless another part of the project specifically requires it.

## Run the experiment

Run these commands from the Ubuntu terminal. Adjust the project path if your folder is named differently.

### 1. Start the Mininet topology

```bash
sudo mn --custom /home/mohammed_abrar_a/ditributed-log-aggregation/topology/log_topology.py --topo logtopo --switch ovsbr --link tc
```

At the `mininet>` prompt, check connectivity:

```text
pingall
```

Expected result for a healthy topology: `0% dropped (6/6 received)`.

### 2. Start the log server on h3

```text
h3 python3 /home/mohammed_abrar_a/ditributed-log-aggregation/server/log_server.py > /tmp/priority_server.log 2>&1 &
```

### 3. Start the UDP iperf receiver on h3

```text
h3 iperf -s -u -p 5001 > /tmp/iperf_receiver.txt 2>&1 &
```

### 4. Generate background UDP traffic from h2

```text
h2 iperf -c 10.0.0.3 -u -p 5001 -b 2M -t 20 > /tmp/iperf_sender.txt 2>&1 &
```

This requests 2 Mbps of UDP traffic. The shaped 100 Kbps inter-switch link limits the throughput that can actually cross the bottleneck.

### 5. Run the delivery test from h1

Run this immediately after starting the background traffic:

```text
h1 python3 /home/mohammed_abrar_a/ditributed-log-aggregation/tests/test_delivery.py
```

The test sends 100 UDP log packets and counts matching ACKs received within its configured timeout.

### 6. Run a baseline without background traffic

Stop iperf traffic:

```text
h2 pkill iperf
```

Then run the same delivery test:

```text
h1 python3 /home/mohammed_abrar_a/ditributed-log-aggregation/tests/test_delivery.py
```

## Experimental results

The following values are the outputs reported during the recorded lab session. The delivery test uses a 2-second ACK collection timeout.

| Measurement | Background traffic active | Background traffic stopped |
|---|---:|---:|
| Bottleneck setting | 100 Kbps | 100 Kbps |
| Background UDP traffic | 2 Mbps requested | Stopped |
| Log packets sent by client | 100 | 100 |
| ACKs received within timeout | 0 | 100 |
| ACK rate within timeout | 0% | 100% |
| Test measurement time | 2.070 s | 2.017 s |

### Server-side observation

During the congested run, the server log was inspected and the command `grep -c "Delivery test packet" /tmp/priority_server.log` returned `100`. The server log also showed delivery-test messages. However, the log file was not cleared immediately before the run, so this count is not a clean isolated measurement of that run.

### Interpretation and limitations

- In the congested run, the client received no matching ACKs within its 2-second timeout.
- In the no-background-traffic run, the client received all 100 ACKs within the timeout.
- An unacknowledged packet is **not automatically proof that the original log packet was lost**. The original UDP packet may have reached the server while its ACK was delayed or dropped.
- The current ACK is sent after queue insertion, not after disk persistence.
- The iperf output recorded during the 100 Kbps experiment showed a receiver rate of about 94.8 Kbps. Its displayed datagram-loss count and percentage were inconsistent, so that loss percentage should be re-measured before being quoted as a final metric.
- Repeat the tests with the server log cleared before each run, and use a longer ACK timeout or per-packet timestamps to distinguish delayed ACKs from missing ACKs.

## Screenshots

Add your own screenshots from the Ubuntu/Mininet session to the `screenshots/` folder. Suggested evidence:

1. `01-topology-pingall.png` — Mininet topology running and `pingall` showing 0% dropped.
2. `02-server-running.png` — log server running on h3.
3. `03-iperf-congestion.png` — iperf client/server output during the background traffic test.
4. `04-congested-delivery.png` — 100-packet delivery report during congestion.
5. `05-baseline-delivery.png` — 100-packet delivery report after stopping iperf.
6. `06-server-log.png` — server log showing received delivery-test messages.

To capture a screenshot in Ubuntu, use the system screenshot tool or press `PrtSc`. Save the images with the filenames above inside this repository's `screenshots/` folder. Do not use fabricated or recreated output as experiment evidence.

## Future improvements

- Clear or rotate server logs before each test so each run has an isolated packet count.
- Add send/receive counters and per-packet timing to measure ACK delay.
- Distinguish packets received by the server, packets persisted to disk, and ACKs received by the client.
- Repeat experiments at multiple bottleneck rates and traffic loads.
- Add reproducible plots comparing delivery and acknowledgement results.
