# Tech Stack

[← README](../README.md) · Related: [Architecture](architecture.md) · [Roadmap](roadmap.md) · [References](references.md)

- **Collection daemon**: Python (prototyping) → Rust (`electrum-client` crate) for production
- **Protocol reference**: https://electrum-protocol.readthedocs.io/en/latest/
- **Transport**: Raw JSON-RPC over TCP/SSL; Tor via SOCKS5
- **Storage**: SQLite (M0) → TimescaleDB (PostgreSQL) or InfluxDB
- **Analysis**: Python (pandas, scipy, scikit-learn for clustering)
- **Visualization**: Grafana dashboards for live monitoring; static reports for cluster analysis
