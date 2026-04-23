# Roadmap

[← README](../README.md) · Related: [Architecture](architecture.md) · [Tech stack](tech-stack.md) · [References](references.md)

## M0: Local Prototype (run on your machine, no infra needed)

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

## M1: Server Discovery & Expanded Collection
- [ ] Server list scraper (1209k.com HTML parse)
- [ ] `server.peers.subscribe` for peer discovery
- [ ] `server.features` collection
- [ ] Scale to 200-500 servers
- [ ] Deploy to EC2 t3.small for continuous collection

## M2: Full Data Collection
- [ ] Tor support (SOCKS5 proxy for `.onion` servers)
- [ ] Migrate SQLite → TimescaleDB
- [ ] Grafana dashboard for live server status
- [ ] Stale block probing during live fork races

## M3: Sybil Analysis
- [ ] Pairwise correlation engine for block timing
- [ ] Downtime correlation detector
- [ ] Fee histogram similarity analysis (Wasserstein distance)
- [ ] Clustering pipeline (DBSCAN) with configurable thresholds
- [ ] Report generator: suspected sybil clusters with evidence scores

## M4: Advanced
- [ ] Multi-vantage point deployment (2-3 additional collectors in different ASes)
- [ ] AS/IP enrichment for clearnet servers
- [ ] Public dashboard or API for community use
- [ ] Rust rewrite of collection daemon for production
