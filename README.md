# Electrum Server Sybil Detector

## Module: `electrum-sybil-detector`

**Parent project:** bitcoin-node-scanner
**Status:** Draft
**Author:** ifuensan
**Date:** 2026-04-10

## Problem Statement

Surveillance companies (e.g. Chainalysis) likely operate multiple public Electrum servers to collect user addresses and link them to IPs, enhancing their address-clustering datasets. An Electrum wallet connects to ~10 servers but only leaks its addresses to one, so running many servers increases coverage. To reduce costs, operators likely share a single Bitcoin Core backend across multiple Electrum frontends, or run one Electrum server listening on multiple IPs/ports/domains. This shared infrastructure creates detectable behavioral correlations.

## Objective

Build a long-running data collection and analysis pipeline that connects to all known public Electrum servers, records behavioral fingerprints over time, and identifies clusters of servers likely operated by the same entity — especially surveillance operators.

## Architecture

### 1. Server Discovery

IRC-based peer discovery was removed in ElectrumX 1.2.1. Modern discovery is peer-to-peer: servers connect to each other directly and exchange peer lists via RPC.

- **Seeds**: scrape server list from https://1209k.com/bitcoin-eye/ele.php?chain=btc + parse hardcoded peer list from Electrum wallet source code (`lib/coins.py` in ElectrumX, `servers.json` / `servers_testnet.json` in Electrum wallet)
- **Snowball via `server.peers.subscribe`**: connect to seeds, collect their known peers, connect to those, repeat. A few rounds covers the reachable network.
- **`server.features`**: each peer advertises hosts, ports, genesis hash, pruning limits, and protocol version range — useful both for discovery and fingerprinting
- Maintain a registry of known servers (clearnet + Tor `.onion`)
- Note: ElectrumX already limits peers from similar IP subnets in `server.peers.subscribe` responses as anti-sybil measure — a sophisticated sybil operator needs IPs across different subnets, which is itself a detectable pattern via ASN analysis

### 2. Data Collection Daemon

Long-running process that maintains persistent connections to all discovered servers and records the following data points with sub-second timestamps (UTC):

#### Block Notifications (highest priority)
- Subscribe via `blockchain.headers.subscribe`
- Record: server_id, block_height, block_hash, notification_timestamp_ms
- **Critical during fork races**: record all competing tips and timing

#### Server Metadata
- `server.version` → protocol version, server software, software version
- `server.features` → `ServerFeaturesRes` (hosts, ports, genesis_hash, hash_function, pruning, protocol_min/max)
- `server.banner` → welcome/help text
- `server.donation_address` → donation address (same address across "different" servers = strong signal)

#### Fee Data
- `blockchain.estimatefee(n)` for n ∈ {1, 2, 3, 5, 10, 25, 50, 100, 144, 504, 1008} — include unusual values to trigger edge cases
- `blockchain.relayfee` — record value and any changes over time
- `mempool.get_fee_histogram` — full histogram snapshot at regular intervals (e.g. every 30s)

#### Availability & Latency
- Connection uptime/downtime windows per server
- Ping RTT (`server.ping`)
- Reconnection behavior and timing

#### Stale Block Probing (experimental)
- During live fork races: query `blockchain.block.header(height)` on all servers simultaneously to detect which fork each server follows
- Cross-reference with known stale blocks from https://github.com/bitcoin-data/stale-blocks
- Note: `blockchain.transaction.get_merkle` takes height, so merkle proof probing for stale blocks is not directly viable

### 3. Storage

Time-series database (InfluxDB or TimescaleDB over PostgreSQL) with:

- `block_notifications(server_id, height, hash, timestamp_ms)`
- `server_metadata(server_id, timestamp, version, features_json, banner, donation_address)`
- `fee_estimates(server_id, timestamp, block_target, fee_rate)`
- `relay_fees(server_id, timestamp, relay_fee)`
- `fee_histograms(server_id, timestamp, histogram_json)`
- `availability(server_id, timestamp, event_type, latency_ms)`

Retention: indefinite for block notifications and metadata; 90 days raw for high-frequency data (fee histograms, pings), downsampled after.

### 4. Sybil Analysis Engine

#### Correlation Metrics

| Signal | Method | Strength |
|---|---|---|
| Block notification timing | Pairwise Δt distribution during races | Very high |
| Synchronized downtime | Overlapping offline windows | High |
| Identical fee histograms | Exact match or Wasserstein distance < ε | High |
| Same donation address | Exact match | Very high (but easily avoided) |
| Identical banners/versions | String similarity | Medium |
| Correlated fee estimates | Time-series cross-correlation | Medium-high |
| Same relay_fee transitions | Simultaneous change events | Medium-high |
| Same `server.features` | Structural diff | Medium |

#### Clustering

- Build a similarity matrix across all server pairs using weighted combination of the above signals
- Apply hierarchical or DBSCAN clustering to identify sybil groups
- For each cluster, estimate likelihood of shared backend (single Bitcoin Core instance)
- Flag clusters where >N servers resolve to the same AS or IP range

#### Tor Servers

- Connect via SOCKS5 proxy
- Treat as separate cohort (no IP-based correlation available)
- All behavioral signals still apply
- Note: even without IP linkage, leaked addresses can still be clustered together by the operator

### 5. Multi-Vantage Collection (optional)

Run collectors from different ASes/geographies to detect:
- Servers that behave differently based on connecting IP
- Geo-targeted surveillance (e.g. only logging connections from certain regions)
- DNS-based load balancing revealing shared infrastructure

## Tech Stack

- **Collection daemon**: Python (prototyping) → Rust (`electrum-client` crate) for production
- **Protocol reference**: https://electrum-protocol.readthedocs.io/en/latest/
- **Transport**: Raw JSON-RPC over TCP/SSL; Tor via SOCKS5
- **Storage**: SQLite (M0) → TimescaleDB (PostgreSQL) or InfluxDB
- **Analysis**: Python (pandas, scipy, scikit-learn for clustering)
- **Visualization**: Grafana dashboards for live monitoring; static reports for cluster analysis

## Milestones

### M0: Local Prototype (run on your machine, no infra needed)

Single Python script (`electrum_monitor.py`), stdlib only (no pip deps), SQLite storage.

- [ ] Hardcoded seed server list (~10-20 known servers)
- [ ] Asyncio connection manager: connect, reconnect with exponential backoff, TCP/SSL
- [ ] `blockchain.headers.subscribe` — record block notifications with ms timestamps
- [ ] `server.version`, `server.banner`, `server.donation_address` — collect on connect
- [ ] `server.ping` — periodic RTT recording
- [ ] `blockchain.estimatefee(n)` for key block targets — periodic polling
- [ ] `blockchain.relayfee` — periodic polling
- [ ] `mempool.get_fee_histogram` — periodic polling
- [ ] Uptime/downtime event logging per server
- [ ] SQLite schema covering all collected data
- [ ] CLI flags: `--report` (summary), `--dump-blocks` (CSV export for analysis)
- [ ] Runs indefinitely, Ctrl+C graceful shutdown

**NOT in M0**: Tor, server discovery (peer subscribe snowball/1209k scraping), analysis engine, Grafana.
**Infra**: your laptop. SQLite file grows ~50-100 MB/month with 20 servers.

### M1: Server Discovery & Expanded Collection
- [ ] Server list scraper (1209k.com HTML parse)
- [ ] `server.peers.subscribe` for peer discovery
- [ ] `server.features` collection
- [ ] Scale to 200-500 servers
- [ ] Deploy to EC2 t3.small for continuous collection

### M2: Full Data Collection
- [ ] Tor support (SOCKS5 proxy for `.onion` servers)
- [ ] Migrate SQLite → TimescaleDB
- [ ] Grafana dashboard for live server status
- [ ] Stale block probing during live fork races

### M3: Sybil Analysis
- [ ] Pairwise correlation engine for block timing
- [ ] Downtime correlation detector
- [ ] Fee histogram similarity analysis (Wasserstein distance)
- [ ] Clustering pipeline (DBSCAN) with configurable thresholds
- [ ] Report generator: suspected sybil clusters with evidence scores

### M4: Advanced
- [ ] Multi-vantage point deployment (2-3 additional collectors in different ASes)
- [ ] AS/IP enrichment for clearnet servers
- [ ] Public dashboard or API for community use
- [ ] Rust rewrite of collection daemon for production

## References

- Electrum Protocol Specification: https://electrum-protocol.readthedocs.io/en/latest/
- ElectrumX Peer Discovery: https://electrumx-spesmilo.readthedocs.io/en/latest/peer_discovery.html
- Rust electrum-client: https://docs.rs/electrum-client/0.23.1/electrum_client/
- Server list: https://1209k.com/bitcoin-eye/ele.php?chain=btc
- Stale blocks dataset: https://github.com/bitcoin-data/stale-blocks
- Original idea: b10c (0xb10c)
