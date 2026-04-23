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

## Documentation

- [Architecture](docs/architecture.md) — discovery, collection daemon, storage, sybil analysis engine, multi-vantage collection
- [Tech stack](docs/tech-stack.md) — languages, transport, storage, analysis, visualization
- [Roadmap](docs/roadmap.md) — milestones M0 → M4
- [References](docs/references.md) — protocol specs, datasets, prior art
