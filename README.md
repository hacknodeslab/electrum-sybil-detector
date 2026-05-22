# Electrum Server Sybil Detector

* **Project:** `electrum-sybil-detector`
* **Lab:** HackNodes Lab
* **Status:** Draft (research output — tool → dataset → paper)
* **Author:** ifuensan
* **Date:** 2026-04-10

## Problem Statement

Surveillance companies (e.g. Chainalysis) likely operate multiple public Electrum servers to collect user addresses and link them to IPs, enhancing their address-clustering datasets. An Electrum wallet connects to ~10 servers but only leaks its addresses to one, so running many servers increases coverage. To reduce costs, operators likely share a single Bitcoin Core backend across multiple Electrum frontends, or run one Electrum server listening on multiple IPs/ports/domains. This shared infrastructure creates detectable behavioral correlations.

## Objective

Build a long-running data collection and analysis pipeline that connects to all known public Electrum servers, records behavioral fingerprints over time, and identifies clusters of servers likely operated by the same entity — especially surveillance operators.

## Target server implementations

Public-facing Electrum server implementations fingerprinted by the detector:

<table>
  <tr>
    <td align="center" width="20%">
      <a href="https://github.com/kyuupichan/electrumx">
        <b>ElectrumX</b>
      </a><br>
      <sub>Python · MIT</sub>
    </td>
    <td align="center" width="20%">
      <a href="https://github.com/romanz/electrs">
        <img src="docs/assets/logos/electrs.svg" height="48" alt="electrs logo"><br>
        <b>electrs</b>
      </a><br>
      <sub>Rust · MIT</sub>
    </td>
    <td align="center" width="20%">
      <a href="https://github.com/Blockstream/electrs">
        <b>Blockstream electrs</b>
      </a><br>
      <sub>Rust · MIT · Esplora backend</sub>
    </td>
    <td align="center" width="20%">
      <a href="https://github.com/cculianu/Fulcrum">
        <img src="docs/assets/logos/fulcrum.png" height="48" alt="Fulcrum logo"><br>
        <b>Fulcrum</b>
      </a><br>
      <sub>C++ · GPLv3</sub>
    </td>
    <td align="center" width="20%">
      <a href="https://github.com/chris-belcher/electrum-personal-server">
        <b>Electrum Personal Server</b>
      </a><br>
      <sub>Python · MIT</sub>
    </td>
  </tr>
</table>

## Documentation

- [Architecture](docs/architecture.md) — discovery, collection daemon, storage, sybil analysis engine, multi-vantage collection
- [Tech stack](docs/tech-stack.md) — languages, transport, storage, analysis, visualization
- [Roadmap](docs/roadmap.md) — milestones M0 → M4
- [References](docs/references.md) — protocol specs, datasets, prior art
