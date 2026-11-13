# Congestion experiment — recorded results

Date recorded: 31 October 2026

## Client-side delivery test

| Metric | Background traffic active | Background traffic stopped |
|---|---:|---:|
| Bottleneck setting | 100 Kbps | 100 Kbps |
| Background UDP traffic | 2 Mbps requested | Stopped |
| Log packets sent | 100 | 100 |
| ACKs received within timeout | 0 | 100 |
| ACK rate within timeout | 0% | 100% |
| Measurement time | 2.070 s | 2.017 s |

## Server-side observation

During the congested run, `grep -c "Delivery test packet" /tmp/priority_server.log` returned `100`, and the server log showed delivery-test messages. The log file was not cleared immediately before the run, so this is not a clean isolated count for that run.

## Interpretation

The congested run produced zero client acknowledgements within the test's 2-second timeout, while the baseline run produced 100/100 acknowledgements. This does not prove that all original log datagrams were lost: the server may receive a log while its ACK is delayed or dropped.

The server sends the ACK after accepting a packet into its in-memory queue, not after confirming disk persistence.

The iperf output from the 100 Kbps experiment reported approximately 94.8 Kbps at the receiver. Its displayed datagram-loss count and percentage were inconsistent; re-run and verify this measurement before reporting a UDP loss percentage.
