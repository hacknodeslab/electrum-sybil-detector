# Architecture

[← README](../README.md) · Related: [Tech stack](tech-stack.md) · [Roadmap](roadmap.md) · [References](references.md)

## 1. Server Discovery

IRC-based peer discovery was removed in ElectrumX 1.2.1. Modern discovery is peer-to-peer: servers connect to each other directly and exchange peer lists via RPC.

- **Seeds**: scrape server list from https://1209k.com/bitcoin-eye/ele.php?chain=btc + parse hardcoded peer list from Electrum wallet source code (`lib/coins.py` in ElectrumX, `servers.json` / `servers_testnet.json` in Electrum wallet)
- **Snowball via `server.peers.subscribe`**: connect to seeds, collect their known peers, connect to those, repeat. A few rounds covers the reachable network.
- **`server.features`**: each peer advertises hosts, ports, genesis hash, pruning limits, and protocol version range — useful both for discovery and fingerprinting
- Maintain a registry of known servers (clearnet + Tor `.onion`)
- Note: ElectrumX already limits peers from similar IP subnets in `server.peers.subscribe` responses as anti-sybil measure — a sophisticated sybil operator needs IPs across different subnets, which is itself a detectable pattern via ASN analysis

## 2. Data Collection Daemon

Long-running process that maintains persistent connections to all discovered servers and records the following data points with sub-second timestamps (UTC):

### Block Notifications (highest priority)
- Subscribe via `blockchain.headers.subscribe`
- Record: server_id, block_height, block_hash, notification_timestamp_ms
- **Critical during fork races**: record all competing tips and timing

### Server Metadata
- `server.version` → protocol version, server software, software version
- `server.features` → `ServerFeaturesRes` (hosts, ports, genesis_hash, hash_function, pruning, protocol_min/max)
- `server.banner` → welcome/help text
- `server.donation_address` → donation address (same address across "different" servers = strong signal)

### Fee Data
- `blockchain.estimatefee(n)` for n ∈ {1, 2, 3, 5, 10, 25, 50, 100, 144, 504, 1008} — include unusual values to trigger edge cases
- `blockchain.relayfee` — record value and any changes over time
- `mempool.get_fee_histogram` — full histogram snapshot at regular intervals (e.g. every 30s)

### Availability & Latency
- Connection uptime/downtime windows per server
- Ping RTT (`server.ping`)
- Reconnection behavior and timing

### Stale Block Probing (experimental)
- During live fork races: query `blockchain.block.header(height)` on all servers simultaneously to detect which fork each server follows
- Cross-reference with known stale blocks from https://github.com/bitcoin-data/stale-blocks
- Note: `blockchain.transaction.get_merkle` takes height, so merkle proof probing for stale blocks is not directly viable

## 3. Storage

Time-series database (InfluxDB or TimescaleDB over PostgreSQL) with:

- `block_notifications(server_id, height, hash, timestamp_ms)`
- `server_metadata(server_id, timestamp, version, features_json, banner, donation_address)`
- `fee_estimates(server_id, timestamp, block_target, fee_rate)`
- `relay_fees(server_id, timestamp, relay_fee)`
- `fee_histograms(server_id, timestamp, histogram_json)`
- `availability(server_id, timestamp, event_type, latency_ms)`

Retention: indefinite for block notifications and metadata; 90 days raw for high-frequency data (fee histograms, pings), downsampled after.

## 4. Sybil Analysis Engine

### Correlation Metrics

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

### Clustering

- Build a similarity matrix across all server pairs using weighted combination of the above signals
- Apply hierarchical or DBSCAN clustering to identify sybil groups
- For each cluster, estimate likelihood of shared backend (single Bitcoin Core instance)
- Flag clusters where >N servers resolve to the same AS or IP range

### Tor Servers

- Connect via SOCKS5 proxy
- Treat as separate cohort (no IP-based correlation available)
- All behavioral signals still apply
- Note: even without IP linkage, leaked addresses can still be clustered together by the operator

## 5. Multi-Vantage Collection (optional)

Run collectors from different ASes/geographies to detect:
- Servers that behave differently based on connecting IP
- Geo-targeted surveillance (e.g. only logging connections from certain regions)
- DNS-based load balancing revealing shared infrastructure
