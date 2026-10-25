# Distributed Log Aggregation Using Software-Defined Networking

## 1. Project Overview

This project implements a distributed log aggregation system using Python UDP sockets and a Software-Defined Networking (SDN) environment.

The system collects log messages from network hosts, classifies them by severity, and stores them in separate log files.

## 2. Technologies Used

- Ubuntu Linux
- Python 3
- UDP sockets
- Mininet
- Open vSwitch
- OS-Ken SDN controller
- OpenFlow 1.3

## 3. Project Structure

```text
ditributed-log-aggregation/
├── client/
│   └── log_client.py
├── controller/
│   └── log_controller.py
├── logs/
│   ├── critical.log
│   ├── error.log
│   ├── info.log
│   ├── received.log
│   └── warning.log
├── results/
│   └── test_results.txt
├── server/
│   ├── log_server.py
│   └── log_server_backup.py
├── tests/
│   ├── test_client.py
│   └── test_priority.py
└── topology/
    └── log_topology.py
```

## 4. Log Severity Levels

The system supports four log severity levels:

| Severity | Priority |
|---|---:|
| CRITICAL | 1 |
| ERROR | 2 |
| WARNING | 3 |
| INFO | 4 |

Lower priority numbers represent higher severity.

## 5. Testing

Run the client tests:

```bash
python3 tests/test_client.py
```

Run the priority tests:

```bash
python3 tests/test_priority.py
```

The reported test results show that all three client tests and the priority mapping checks passed.

## 6. Network Verification

The Mininet topology was tested using `pingall`.

The recorded result was:

```text
*** Results: 0% dropped (6/6 received)
```

UDP log delivery was also tested between a Mininet host and the log server.

## 7. Log Storage

The system stores log messages in separate files:

- `logs/critical.log` — CRITICAL messages
- `logs/error.log` — ERROR messages
- `logs/warning.log` — WARNING messages
- `logs/info.log` — INFO messages
- `logs/received.log` — received log messages

## 8. Test Results

See `results/test_results.txt` for the recorded client and priority test results.

## 9. How to Run the Project

### Prerequisites

The project requires Ubuntu Linux, Python 3, Mininet, Open vSwitch, and the OS-Ken SDN controller environment.

### Step 1: Start the SDN Controller

Open Terminal 1 and run:

```bash
source ~/ryu311-env/bin/activate
cd ~/ditributed-log-aggregation
osken-manager controller/log_controller.py
```

Keep this terminal running.

### Step 2: Start the Mininet Topology

Open Terminal 2 and run:

```bash
cd ~/ditributed-log-aggregation
sudo mn --custom topology/log_topology.py --topo logtopo --switch ovs,protocols=OpenFlow13 --controller=remote,ip=127.0.0.1,port=6653
```

At the `mininet>` prompt, verify connectivity:

```text
pingall
```

The expected result from the verified setup is 0% packet loss.

### Step 3: Start the Log Server

At the `mininet>` prompt, run:

```text
h3 python3 server/log_server.py
```

Keep the server running.

### Step 4: Send a Test Log

Open Terminal 3 in Ubuntu and run:

```bash
sudo mnexec -a $(pgrep -f 'mininet:h1' | head -n 1) python3 ~/ditributed-log-aggregation/client/log_client.py INFO "Test log from h1"
```

The client should report that the log was sent to `10.0.0.3:9999`. Check the server terminal for the received message.

### Step 5: Run the Automated Tests

In an Ubuntu terminal, run:

```bash
cd ~/ditributed-log-aggregation
python3 tests/test_client.py
python3 tests/test_priority.py
```

Both test scripts should pass.

### Step 6: Inspect the Logs

Inspect the stored logs with:

```bash
cat logs/received.log
cat logs/info.log
cat logs/warning.log
cat logs/error.log
cat logs/critical.log
```
