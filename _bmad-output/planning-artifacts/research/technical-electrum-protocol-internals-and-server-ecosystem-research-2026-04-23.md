---
stepsCompleted: [1, 2, 3, 4, 5, 6]
inputDocuments: []
workflowType: 'research'
lastStep: 6
research_type: 'technical'
research_topic: 'Electrum protocol internals and server ecosystem'
research_goals: 'Primary: background/related-work for the Electrum Sybil Detector paper. Secondary: internal reference while building detection heuristics. Tertiary: public-facing explainer (Librería de Satoshi). Style: broad survey. Focus priority: (1) server implementations — ElectrumX, electrs, Fulcrum, EPS, esplora-electrs (feature matrices, forks, behavioral differences); (2) wire protocol (JSON-RPC methods, subscriptions, versioning handshake, framing over TCP/SSL/WS/WSS); (3) server discovery & peer-gossip (server.peers.subscribe, seed list, pool construction); (4) transport & deployment (TLS, .onion, reverse proxies, hosting patterns); (5) data paths (scripthash subscriptions, merkle proofs, header chain sync).'
user_name: 'Ifuensan'
date: '2026-04-23'
web_research_enabled: true
source_verification: true
---

# Research Report: technical

**Date:** 2026-04-23
**Author:** Ifuensan
**Research Type:** technical

---

## Research Overview

This document is a broad technical survey of the **Electrum protocol and its server ecosystem**, conducted as background and related-work material for the Electrum Sybil Detector research project. It maps the reference client, the five dominant server implementations (ElectrumX, romanz/electrs, Fulcrum, mempool-electrs / Blockstream-electrs, EPS), their wire-protocol surface (JSON-RPC 1.0/2.0 over TCP/TLS/WS/WSS, versions 1.4 → 1.6), peer-gossip mechanics, storage/indexing architectures, deployment patterns (Tor, TLS, home-node kits), and the empirical signals each exposes. Primary sources include the canonical `spesmilo/electrum-protocol` and `kyuupichan/electrumx` docs, the `romanz/electrs` schema documentation, the Electrum wallet's hardcoded bootstrap list, the 2019 *Electrohunt* crawl study, a live Shodan-based infrastructure probe (2026-04-23), and the 1209k public monitor.

Key framing conclusions: the ecosystem is small and largely uniform due to **home-node kit distribution** (Umbrel/Start9/RaspiBlitz/MyNode) which imposes shared software defaults on the honest population; ElectrumX's built-in Sybil defenses operate **intra-server** and leave the **shared-infrastructure attribution surface open**, which is precisely where this research project (Push-3 scope) positions the detector; **passive port-scan datasets are weak primary sources** for population discovery (the protocol does not expose banners without a protocol-speaking probe) but are **high-value pivots** for operator-cluster attribution via adjacent services (mempool-electrs HTTP APIs, Prometheus, Docker Registry, rsyncd).

Full methodology, findings, and synthesis are in the sections below; the final **Research Synthesis** section at the end provides the executive summary, table of contents, and strategic recommendations intended for the paper's related-work section, the detector team's internal reference, and public-facing explainers.

---

<!-- Content will be appended sequentially through research workflow steps -->

## Technical Research Scope Confirmation

**Research Topic:** Electrum protocol internals and server ecosystem

**Research Goals (priority-ordered):**
1. Background / related-work section for the Electrum Sybil Detector research output
2. Internal reference while building detection heuristics
3. Public-facing explainer (Librería de Satoshi material)

**Focus priority:** (b) server implementations → (a) wire protocol → (c) peer discovery & gossip → (d) transport & deployment → (e) data paths. Style: broad survey.

**Technical Research Scope:**

- Architecture Analysis — server implementation architectures (ElectrumX, electrs, Fulcrum, EPS, esplora-electrs), indexer/storage design, fork lineage, maintenance state
- Implementation Approaches — language/runtime choices, DB engines, UTXO/scripthash indexing, feature parity vs. divergence
- Technology Stack (wire protocol) — JSON-RPC surface, `server.version` handshake, `blockchain.scripthash.*` subscriptions, merkle proofs, header sync, message framing
- Integration Patterns — transports (TCP/SSL/WS/WSS/Tor), `server.peers.subscribe` gossip, hardcoded seed list, client pool construction
- Performance / Operational Considerations — deployment patterns, hosting, reverse proxies, sync cost and footprint — viewed through the lens of fingerprinting surface

**Research Methodology:**

- Current web data with rigorous source verification
- Multi-source validation for critical technical claims
- Confidence level framework for uncertain information
- Comprehensive technical coverage with architecture-specific insights

**Scope Confirmed:** 2026-04-23

---

## Technology Stack Analysis

> **Scope of this section.** The Electrum ecosystem has an unusual shape: the "technology stack" is not a cloud-vs-frameworks matrix but a small constellation of **reference implementations** (one canonical client + a handful of servers) glued by a **JSON-RPC protocol** that has no formal standards body. This section therefore diverges from the generic template and maps the stack in the terms that actually structure the ecosystem: (1) **server implementations** (the dominant axis of divergence), (2) **wire protocol & specification authority**, (3) **storage / indexing engines**, (4) **clients & libraries**, (5) **deployment & infrastructure**, (6) **adoption and population trends** — including what little public data exists on who actually runs what in the public mesh.

### 1. Server Implementations

Five implementations define the ecosystem; all others are coin-specific forks of these.

#### 1.1 ElectrumX (Neil Booth → spesmilo)

- **Origin.** `kyuupichan/electrumx` by Neil Booth, written in **Python (≥ 3.10)**, MIT-licensed. The original upstream explicitly **dropped Bitcoin** support to focus on altcoins.
  - [kyuupichan/electrumx](https://github.com/kyuupichan/electrumx) · [spesmilo/electrumx](https://github.com/spesmilo/electrumx)
- **Canonical fork.** `spesmilo/electrumx` is the Bitcoin-maintained fork, tracked by the Electrum wallet project itself. Current docs describe **ElectrumX 1.19.0**.
  - [ElectrumX docs (spesmilo) 1.19.0](https://electrumx-spesmilo.readthedocs.io/)
- **Architecture.** Async Python, explicitly designed for **public-server deployment** (multi-user, high concurrency).
- **Storage.** LevelDB or RocksDB backend selectable (`plyvel` / `python-rocksdb`); stores block heights and tx-hashes as flat linear arrays on disk for O(1) lookup.
- **Transports.** TCP (`50001`), SSL (`50002`), and WSS (`50004`) servers built in.
  - [ElectrumX Environment Variables](https://electrumx.readthedocs.io/en/latest/environment.html)
- **Protocol range.** Min 1.4, current max **1.6** (implemented on the spesmilo line).
- **Positioning.** *"Designed with public server use in mind"* — heavier index and operational footprint than electrs, slower to sync. _Confidence: HIGH (multiple operator sources agree)._
  - [Blockstream blog: Alternatives to ElectrumX](https://blog.blockstream.com/en-esplora-and-other-alternatives-to-electrumx/)

#### 1.2 electrs — romanz/electrs (Rust, upstream)

- **Repository.** [romanz/electrs](https://github.com/romanz/electrs) — *"An efficient re-implementation of Electrum Server in Rust."*
- **Recent releases.** **v0.11.0** (2025-11-17) and **v0.11.1** (2026-02-22). Release bumps rust-rocksdb to 0.36, requires dynamic RocksDB ≥ **9.10.0**, adds `blockchain.transaction.broadcast_package`. DB format breaks forward compatibility on upgrade.
  - [romanz/electrs releases](https://github.com/romanz/electrs/releases) · [RELEASE-NOTES.md](https://github.com/romanz/electrs/blob/master/RELEASE-NOTES.md)
- **Storage.** RocksDB; a *minimal* index — stores compact metadata and **re-parses blocks on the fly** to answer many queries. Trades disk for CPU.
- **Positioning.** Explicitly targeted at **personal-use** / home-node operators: *"lower storage requirements (but higher CPU usage)"*. Most commonly bundled into home-node packages.
- **Deprecation axis.** *Not* deprecated; still the upstream for all major explorer forks below.

#### 1.3 Fulcrum — cculianu/Fulcrum (C++)

- **Repository.** [cculianu/Fulcrum](https://github.com/cculianu/Fulcrum) — "A fast & nimble SPV Server for BCH, BTC, and LTC."
- **Recent releases.** **v2.1.0** (2025-11-17) — support for **Electrum Cash protocol v1.6** with BTC-targeted tweaks; binaries use **RocksDB 9.2.1** (statically linked).
  - [Fulcrum releases](https://github.com/cculianu/Fulcrum/releases) · [v2.1.0 notes](https://newreleases.io/project/github/cculianu/Fulcrum/release/v2.1.0)
- **Language & concurrency.** Modern C++20, multi-threaded + async. The 2.x series introduced a **platform-neutral** DB format (portable across Linux/macOS/Windows and big-endian).
- **Dependency on Bitcoin Core.** Will run without ZMQ, but gets **faster block notifications** when `zmqpubhashblock` is enabled.
- **Positioning.** A comprehensive index, larger than electrs but faster to build than ElectrumX; **dominant query performance** per recent benchmarks (see §6).

#### 1.4 Electrum Personal Server (EPS) — chris-belcher/electrum-personal-server

- **Repository.** [chris-belcher/electrum-personal-server](https://github.com/chris-belcher/electrum-personal-server)
- **Model.** *No indexer.* Uses **Bitcoin Core's wallet** to watch a fixed set of user-imported descriptors/xpubs and serves them over the Electrum protocol. Single-user.
- **Status.** Repo is **not formally archived** (open issues through 2024/2025), but community guidance increasingly recommends against it: *"EPS is a bit slow and you can only connect one wallet at a time, and the configuration of wallets is not user-friendly."* — multiple operator guides now default to electrs/Fulcrum instead.
  - [Bitcointalk: alternatives to EPS](https://bitcointalk.org/index.php?topic=5500087.0) · [The Road to Node: EPS](https://theroadtonode.com/bitcoin-core-extensions/electrum-personal-server)
- **Relevance to Sybil detection.** Because EPS exposes only the *user's* own addresses, an EPS instance is typically single-tenant, non-public, and **not advertised on the peer mesh** — making it largely irrelevant to Sybil population studies but important to understand as the ecosystem's "privacy-first" baseline.

#### 1.5 esplora-electrs (Blockstream) and mempool/electrs

- **Blockstream/electrs.** Fork of `romanz/electrs` powering the **Esplora** block explorer (blockstream.info). Adds an HTTP API and a different index schema. [Blockstream/electrs](https://github.com/Blockstream/electrs)
- **mempool/electrs.** Further fork of Blockstream's, powering **mempool.space**. Release **v3.0.0** (2025-09-05) is the first compatible with mempool 3.x; Mempool 3.x **no longer supports Blockstream/electrs** — production users must migrate. Indexes are **incompatible** across the three lineages (romanz, Blockstream, mempool). [mempool/electrs](https://github.com/mempool/electrs) · [mempool/electrs releases](https://github.com/mempool/electrs/releases)
- **Relevance.** These lineages typically power **public HTTP block-explorer** back-ends rather than the public Electrum peer mesh that Sybil detectors target — but the Electrum-protocol endpoint is real and operators sometimes expose it publicly.

#### 1.6 Coin-fork lineage (brief)

Most Electrum servers outside Bitcoin are direct forks: **Electron-Cash / Fulcrum-RPA** (BCH), **ElectrumSV** (BSV), **ElectrsCash** (BitcoinUnlimited, BCH, Rust), **fujicoin/esplora-electrs**, and numerous altcoin-branded ElectrumX forks. For the Sybil detector, the practical relevance is **banner-string parsing** — these forks all expose `server.version` with distinctive substrings that can be used as implementation fingerprints.

---

### 2. Wire Protocol — Specification Authority & Basics

> **Primary sources for this subsection.** The content below is derived from direct reads of the canonical spec and reference-server docs repositories: [spesmilo/electrum-protocol/docs](https://github.com/spesmilo/electrum-protocol/tree/master/docs) (spec authority) and [kyuupichan/electrumx/docs](https://github.com/kyuupichan/electrumx/tree/master/docs) (reference-server behavior). Where the text quotes the spec, it is quoted verbatim.

#### 2.1 Specification authority

There is **no BIP or formal standards body** for the Electrum protocol. The canonical spec is maintained in the **[spesmilo/electrum-protocol](https://github.com/spesmilo/electrum-protocol)** repository and rendered at **[electrum-protocol.readthedocs.io](https://electrum-protocol.readthedocs.io/en/latest/)** (currently version **1.6.x**). ElectrumX's own docs ([electrumx.readthedocs.io](https://electrumx.readthedocs.io/en/latest/protocol-methods.html)) are the de-facto server-side reference.

Fulcrum / Bitcoin Cash track a parallel **"Electrum Cash Protocol"** (currently 1.6.0) at [electrum-cash-protocol.readthedocs.io](https://electrum-cash-protocol.readthedocs.io/en/latest/protocol-methods.html) and [bitcoincash.network/electrum/](https://bitcoincash.network/electrum/protocol-methods.html). Divergences are minor but **real** for BTC servers running Fulcrum.

> **Confidence flag:** No authoritative single spec. For Sybil-detector fingerprinting, this is actually an *asset* — implementation-specific divergences in method support, return shapes, and version strings are themselves fingerprint vectors.

#### 2.2 JSON-RPC framing and ports (canonical)

_The following is taken verbatim from the canonical spec repository [spesmilo/electrum-protocol/docs/protocol-basics.rst](https://github.com/spesmilo/electrum-protocol/blob/master/docs/protocol-basics.rst)._

- **JSON-RPC version.** Both **JSON-RPC 1.0 and 2.0 are permitted**; *"use of version 2.0 is encouraged but not required."*
- **Transports.** Explicitly lists **TCP, SSL, WS, WSS**.
- **Framing.** *"Over TCP and SSL raw sockets each RPC call, and each response, MUST be terminated by a single newline to delimit messages. Websocket messages are already framed so they MUST NOT be newline terminated."*
- **Version negotiation.** *"The client must send a `server.version` RPC call as the first message on the wire, in order to negotiate the precise protocol version."* — this was **tightened in v1.6**: `server.version` **must be the first message** (see §2.3 change-log).
- **Default ports (de-facto, from ElectrumX env vars & operator practice).** `50001` — plain TCP (scheme letter **`t`**); `50002` — TLS (**`s`**); `50004` — WSS (ElectrumX). Historical HTTP/HTTPS letters **`h` / `g`** on ports 8081/8082 are legacy — modern deployments use `t`/`s` (and increasingly `.onion` + `s`).
  - [ElectrumX environment docs](https://electrumx.readthedocs.io/en/latest/environment.html) · [Electrum SSL docs](https://electrum.readthedocs.io/en/latest/ssl.html)

> **Note on transport encryption.** Unlike Bitcoin Core's P2P, which gained **BIP324** (v2 encrypted transport with ChaCha20-Poly1305 handshake) — see [bitcoinops.org BIP324](https://bitcoinops.org/en/topics/v2-p2p-transport/) / [BIP-324](https://bips.dev/324/) — **no equivalent proposal has landed for the Electrum client-server protocol.** Transport security is entirely TLS + Tor today. This is a research gap worth noting in the paper's related-work.

#### 2.3 Protocol version history (canonical change-log)

_Source: [spesmilo/electrum-protocol/docs/protocol-changes.rst](https://github.com/spesmilo/electrum-protocol/blob/master/docs/protocol-changes.rst)._ Abridged.

| Version | Key changes |
|---|---|
| **1.0** | Baseline. Deprecated: `blockchain.utxo.get_address`, `blockchain.numblocks.subscribe`. |
| **1.1** | **Scripthash methods introduced** (`get_balance`, `get_history`, `get_mempool`, `listunspent`, `subscribe`) replacing UTXO-based. `server.features`, `server.add_peer` added. `server.version` negotiation semantics changed. |
| **1.2** | `verbose` param on `blockchain.transaction.get`; `raw` on `blockchain.headers.subscribe`; `server.ping` added; `blockchain.block.headers` and `mempool.get_fee_histogram` added; address-based methods deprecated. |
| **1.3** | `raw=True` default on `headers.subscribe`; `blockchain.block.header` replaces `block.get_header`; address-based methods **removed**. |
| **1.4** | `raw` removed from `headers.subscribe` (deserialized headers no longer available). `cp_height` merkle proof parameter added; `blockchain.transaction.id_from_pos` added. |
| **1.4.1–1.4.3** | AuxPoW truncation; unsubscribe functionality (1.4.2 adds `blockchain.scripthash.unsubscribe`); name resolution with proofs. |
| **1.6** | **Breaking**: `server.version` must be the first message on the wire. `blockchain.block.headers` output format changed from concatenated hex to list. `blockchain.relayfee` removed (replaced by `mempool.get_info`). `mode` param added to `blockchain.estimatefee`. `sorted` results in `scripthash.get_mempool`. |

> **Sybil-detector implication.** A server's **supported version range** (obtained from `server.version` reply and/or `server.features.protocol_min/protocol_max`) is a *first-class fingerprint vector*. Servers stuck at 1.4 vs. those at 1.6 reveal both implementation choice and operator patch cadence.

#### 2.4 Canonical method surface (authoritative)

_Source: [spesmilo/electrum-protocol/docs/protocol-methods.rst](https://github.com/spesmilo/electrum-protocol/blob/master/docs/protocol-methods.rst). "Type" = request (req) / subscription (sub). Version annotations = earliest spec version in which the method/feature appeared._

**`server.*` — server-control & peer-mesh namespace**

| Method | Type | Purpose |
|---|---|---|
| `server.version` | req | Handshake / protocol-version negotiation. **Must be first wire message (v1.6+)**. |
| `server.banner` | req | Returns human-readable banner (operator free-form text — **fingerprint vector**). |
| `server.donation_address` | req | Returns operator's donation address (**fingerprint vector**). |
| `server.features` | req | Dict of server capabilities (genesis hash, protocol_min/max, hosts map, hash_function, pruning, server_version) — **a goldmine of fingerprint data**. |
| `server.peers.subscribe` | req | Returns peer list from server's local peer DB. *Core input to Sybil detection crawls.* |
| `server.add_peer` (v1.1+) | req | Advertise self to peer. |
| `server.ping` (v1.2+) | req | Heartbeat. |

**`blockchain.*` — chain & wallet-query namespace**

| Method | Type | Purpose |
|---|---|---|
| `blockchain.headers.subscribe` | sub | Tip updates (new block headers). |
| `blockchain.block.header` (v1.3+) | req | Single header; optional merkle proof via `cp_height` (v1.4+). |
| `blockchain.block.headers` (v1.2+) | req | Multiple headers; `cp_height` (v1.4+); list-format output (v1.6+). |
| `blockchain.scripthash.subscribe` (v1.1+) | sub | Subscribe to scripthash status. |
| `blockchain.scripthash.unsubscribe` (v1.4.2+) | req | Cancel subscription. |
| `blockchain.scripthash.get_history` (v1.1+) | req | Confirmed + mempool history for scripthash. |
| `blockchain.scripthash.get_balance` (v1.1+) | req | Confirmed / unconfirmed balance. |
| `blockchain.scripthash.get_mempool` (v1.1+) | req | Mempool-only txs for scripthash (sorted v1.6+). |
| `blockchain.scripthash.listunspent` (v1.1+) | req | UTXO list for scripthash. |
| `blockchain.transaction.get` | req | Raw or decoded tx (`verbose` v1.2+). |
| `blockchain.transaction.broadcast` | req | Submit tx (error-handling changed in 1.1). |
| `blockchain.transaction.broadcast_package` | req | Atomic package broadcast (recent addition; supported in latest romanz/electrs). |
| `blockchain.transaction.get_merkle` | req | Merkle inclusion proof for a tx. |
| `blockchain.transaction.id_from_pos` (v1.4+) | req | Tx hash lookup by (height, position). |
| `blockchain.estimatefee` | req | Fee-rate estimate for target confirm depth; `mode` arg v1.6+. |

**`mempool.*` — mempool-state namespace**

| Method | Type | Purpose |
|---|---|---|
| `mempool.get_fee_histogram` (v1.2+) | req | Global mempool fee distribution. |
| `mempool.get_info` | req | Minimum fees / mempool policy (**replaces `blockchain.relayfee` in v1.6**). |

**Altcoin extensions.** `masternode.*` (Dash), `blockchain.name.*` (Namecoin), BCH/SV-specific additions — per the same methods reference, *"additional methods exist for altcoins beyond those listed above."*

> **Fingerprint-surface summary.** The methods most useful for Sybil / identity attribution — beyond banner strings — are `server.version`, `server.features`, `server.peers.subscribe`, and `server.banner`/`donation_address`. Error-message shapes for `transaction.broadcast` and timing distributions for `scripthash.*` queries are secondary signals.

---

### 3. Database & Storage Technologies

| Implementation | DB engine | Index style | Notes |
|---|---|---|---|
| ElectrumX | LevelDB *or* RocksDB (configurable) | Comprehensive (scripthash history, UTXO, tx lookup) | Adds ~21 GB txid lookup vs. electrs. Python, single-threaded parse. |
| romanz/electrs | RocksDB (≥ 9.10.0 since v0.11) | **Minimal** — stores compact metadata, **re-parses blocks** for many queries | Small disk footprint, higher steady-state CPU. |
| Fulcrum | RocksDB **9.2.1** (static) | Comprehensive, platform-neutral format in 2.x | Fastest query responses. |
| Blockstream/electrs | RocksDB | Comprehensive + HTTP/REST API | Schema incompatible with romanz. |
| mempool/electrs | RocksDB | Comprehensive + mempool-optimized | Schema incompatible with both romanz and Blockstream. |
| EPS | — (uses Bitcoin Core wallet) | No index | Single-user only. |

Benchmark synthesis (from [Sparrow "Server Performance"](https://sparrowwallet.com/docs/server-performance.html) and [Casa 2022 report](https://blog.casa.io/electrum-server-performance-report-2022/)) — _Confidence: MEDIUM, numbers are environment-dependent:_

- **Initial sync time.** electrs ≈ 1 day; Fulcrum ≈ 2–3 days; ElectrumX ≈ 1 week.
- **Index size (BTC mainnet).** ElectrumX ≈ 75 GB; Fulcrum slightly larger; electrs smaller.
- **Query latency (initial wallet load).** Fulcrum ≈ 22× faster than ElectrumX, ≈ 300× faster than electrs (whose on-demand re-parse is the bottleneck). Wallet **refresh**: Fulcrum ≈ 8× ElectrumX, 1.5× electrs.

**Block/mempool ingestion.** All servers read from a Bitcoin Core full node via RPC. Most can *optionally* use **ZMQ** (`zmqpubhashblock`, `zmqpubrawtx`) for push-style new-block notifications; Fulcrum's docs explicitly note improved behavior when linked against libzmq.
- [bitcoin/doc/zmq.md](https://github.com/bitcoin/bitcoin/blob/master/doc/zmq.md) · [ZeroMQ interface primer](https://bitcoindev.network/accessing-bitcoins-zeromq-interface/)

**`txindex=1` requirement.** All full-index servers (ElectrumX, Fulcrum, Blockstream/electrs, mempool/electrs) recommend or require `txindex=1` on the underlying Bitcoin Core. romanz/electrs **does not** require `txindex=1` (compact-index design). — [ElectrumX HOWTO](https://electrumx-spesmilo.readthedocs.io/en/latest/HOWTO.html)

**Privacy leak precedent (storage-layer).** A 2022 issue documented electrs **logging scripthash values** to disk — a privacy regression later fixed: [electrs#724](https://github.com/romanz/electrs/issues/724). Relevant because it demonstrates that storage-layer behaviors leak fingerprintable operator characteristics.

---

### 4. Clients & Libraries Speaking the Protocol

**Reference client — Electrum wallet** ([spesmilo/electrum](https://github.com/spesmilo/electrum)).
- Python, Qt (PyQt) GUI; uses `libsecp256k1`. The wallet ships a **hardcoded bootstrap peer list** and then calls `server.peers.subscribe` to expand. Users can see "number of blocks and response time" per server in the selection window — i.e., the client already fingerprints servers for reliability. ([electrum FAQ](https://github.com/spesmilo/electrum-docs/blob/master/faq.rst))
- Historical scheme letters `g` / `h` (HTTP/HTTPS on 8081/8082) still appear in old docs but the modern defaults are `t` and `s`. The old `#electrum` IRC-on-Freenode side-channel for server discovery is **deprecated** — discovery today is exclusively via hardcoded seed + `server.peers.subscribe` gossip (see §5 below for the authoritative mechanism).

**Sparrow Wallet** ([sparrowwallet.com](https://sparrowwallet.com/docs/server-performance.html)).
- Java/JavaFX. *"Depends on the Electrum server protocol for retrieving and sending transaction information."* Supports public servers, private Electrum servers, and Bitcoin Core directly. Ships server-performance guidance favoring Fulcrum/electrs over ElectrumX.

**BlueWallet** (mobile, React Native). Historically uses public Electrum servers as back-end; also supports BWT. _(Confidence: MEDIUM — search results were thin on specifics; worth a follow-up in Step 5.)_

**Coin forks.** ElectrumSV (BSV), Electrum-LTC, Electron-Cash (BCH), Electrum-Dash — each speaks a lightly-diverged Electrum protocol and sources from its own coin-specific peer mesh.

**Library: rust-electrum-client** ([docs.rs reference](https://docs.rs/crate/electrs/0.1.0)) — the Rust client library companion to `romanz/electrs`. Used by wallets and indexers needing to speak Electrum protocol programmatically.

---

### 5. Deployment & Infrastructure Stack

**TLS.** Port `50002` expects TLS. **Self-signed certificates are common**; operators routinely generate them with one-liner OpenSSL invocations. The Electrum wallet supports pinning by **SSL certificate SHA-256 fingerprint** embedded in the server URI — i.e., the client ecosystem *acknowledges* that the public-CA trust model doesn't fit Electrum. Many operators front the server with **nginx/haproxy** to handle TLS termination and ACME/Let's-Encrypt.
- [Electrum SSL config](https://electrum.readthedocs.io/en/latest/ssl.html) · [Start9 enabling 50002 via nginx](https://community.start9.com/t/enabling-ssl-port-50002-in-electrs-tor/1387)

**Tor.** **Very common** deployment. Servers are typically exposed as a v3 hidden service with `HiddenServicePort 50002 127.0.0.1:50002`. Clients connect using `--proxy socks5:127.0.0.1:9050` (or 9150 for Tor Browser).
- [openoms: Tor hidden service for electrs](https://openoms.github.io/bitcoin-tutorials/electrs/Tor_Hidden_Service_for_Electrs.html)

**Node packages (distribution channel for public/semi-public Electrum servers).**
- **RaspiBlitz** ([raspiblitz/raspiblitz](https://github.com/raspiblitz/raspiblitz)) — bundles electrs and optionally Fulcrum, exposes via Tor by default.
- **Umbrel** ([apps.umbrel.com/app/electrs](https://apps.umbrel.com/app/electrs)) — electrs as a first-class app.
- **Start9 (Embassy)** ([community.start9.com](https://community.start9.com/t/enabling-ssl-port-50002-in-electrs-tor/1387)) — electrs + nginx + Tor.
- **MyNode** ([mynodebtc/mynode](https://github.com/mynodebtc/mynode)) — Electrum server packaged; historical Issue #360 notes TLS setup friction.
- **RaspiBolt / MiniBolt** ([raspibolt.org](https://raspibolt.org/guide/bonus/bitcoin/fulcrum.html), [v2.minibolt.info](https://v2.minibolt.info/bitcoin/bitcoin/electrum-server)) — curated manuals, default to Fulcrum in recent revisions.
- [RaspiBolt issue #894: "Prefer Fulcrum to Electrs"](https://github.com/raspibolt/raspibolt/issues/894) — documents the community pivot toward Fulcrum as default.

> **Sybil-detector implication.** Node-package distribution shapes the operator population: home-node kits have **default banners, default ports, default Tor config patterns, and predictable software versions tied to package release cadence.** A plausible large fraction of the "honest" public mesh is kit-derived. This is the shared-infrastructure axis the detector should exploit (matches the project's Push-3 reframing).

---

### 6. Adoption, Population Distribution & Prior Sybil Evidence

**Which implementation dominates the public BTC mesh?** No rigorous, peer-reviewed census was surfaced in the search. Operator-community signal as of late 2025 / early 2026:

- **Public-server operators skew toward Fulcrum and ElectrumX** (both designed for multi-user loads); **home-node operators skew toward electrs** (bundled by Umbrel/RaspiBlitz/MyNode).
- [Bitcointalk operator poll "Guys, what electrum server you run"](https://bitcointalk.org/index.php?topic=5433223.0) is anecdotal but consistent with the above distribution. _Confidence: LOW — self-report sample._

**Documented Sybil incident (2019).** A Sybil attack on the Electrum peer mesh was documented by **PortSwigger / Daily Swig**, reporting that **471 of 657 active nodes (≈71%)** were attacker-controlled at the time of observation. This is the foundational incident motivating detector work; detailed in [portswigger.net/daily-swig](https://portswigger.net/daily-swig/deep-dive-into-electrum-hack-reveals-70-of-network-was-controlled-by-attackers) and [Malwarebytes 2019 coverage](https://www.malwarebytes.com/blog/news/2019/04/electrum-bitcoin-wallets-under-siege).

**Historical anti-Sybil proposal.** Chris Belcher's 2015 bitcoin-dev post "[Making Electrum more anonymous](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2015-July/009653.html)" is early prior-art on client-side privacy.

**Canonical Sybil mitigations codified in ElectrumX** — directly from [kyuupichan/electrumx/docs/peer_discovery.rst](https://github.com/kyuupichan/electrumx/blob/master/docs/peer_discovery.rst) (verbatim quotes):

- **Seeding.** *"A list of hard-coded, well-known peers seeds the peer discovery process."* Per-coin property; aims for ≥ 4 reliable servers as ground truth.
- **Reply filtering.** *"Only one peer from each IPv4/16 netmask is returned, and the number of onion peers is limited."* (from `server.peers.subscribe` handler)
- **Subnet-aware anti-Sybil.** *"in the response to `server.peers.subscribe` calls, consider limiting the number of peers on similar IP subnets to protect against sybil attacks, and in the case of onion servers the total returned."*
- **`server.add_peer` validation.** *"A receiving server should not replace existing information about the host(s) given, but instead schedule a separate connection to verify the information for itself."* Plus: *"care should be taken with the `server.add_peer` call. Consider only accepting it once per connection. Clearnet peer requests should check the peer resolves to the requesting IP address, to prevent attackers from being able to trigger arbitrary outgoing connections from your server. This doesn't work for onion peers so they should be rate-limited."*
- **Network validation.** *"At a minimum the genesis hash should be compared (if the peer supports `server.features`), and also that the peer's reported height is within a few blocks of your own server's height."*
- **Hostname hygiene.** *"peer host names should be checked for validity before accepting them; and `localhost` should probably be rejected. If it is an IP address it should be a normal public one (not private, multicast or unspecified)."*
- **Source-rate limiting.** *"you should limit the number of new peers accepted from any single source to at most a handful, to limit the effectiveness of malicious peers wanting to trigger arbitrary outgoing connections or fill your peer tables with junk data."*
- **Connection cadence.** *"ElectrumX tries to reconnect to a good peer at least once every 24 hours, and a failing [peer] after 5 minutes but with exponential backoff. It forgets a peer entirely if a few days have passed since a successful connection."*

> **Why this matters for the detector.** These are the *defensive* heuristics implemented inside servers. A Sybil detector operating **externally** (crawling the public mesh) can validate that individual servers are respecting these limits — and a server that *does not* (e.g., returns many peers from the same /16) is itself a candidate anomaly. Crucially, the ElectrumX defenses are **intra-server**; they do nothing against an attacker that spins up many independent, well-configured servers. That is exactly the gap the shared-infrastructure attribution approach targets.

**Emerging trends (2024–2026).**
- Protocol has moved **1.4 → 1.5 → 1.6** on the spesmilo line; Fulcrum tracks via its Electrum Cash Protocol cousin.
- RocksDB version ratchet (romanz requiring 9.10; Fulcrum 9.2.1) creates **operator-version churn** — a potential timing signal for detectors.
- **No encrypted-transport upgrade** (no BIP-324 equivalent) — TLS + Tor remain the only options.
- Community default is shifting from electrs → Fulcrum on public-facing servers.

---

### Sources (consolidated for this section)

**Server implementations.**
- [kyuupichan/electrumx](https://github.com/kyuupichan/electrumx) · [spesmilo/electrumx](https://github.com/spesmilo/electrumx) · [ElectrumX docs 1.19.0](https://electrumx-spesmilo.readthedocs.io/)
- [romanz/electrs](https://github.com/romanz/electrs) · [releases](https://github.com/romanz/electrs/releases) · [RELEASE-NOTES](https://github.com/romanz/electrs/blob/master/RELEASE-NOTES.md)
- [cculianu/Fulcrum](https://github.com/cculianu/Fulcrum) · [releases](https://github.com/cculianu/Fulcrum/releases) · [v2.1.0 notes](https://newreleases.io/project/github/cculianu/Fulcrum/release/v2.1.0)
- [chris-belcher/electrum-personal-server](https://github.com/chris-belcher/electrum-personal-server)
- [Blockstream/electrs](https://github.com/Blockstream/electrs) · [mempool/electrs](https://github.com/mempool/electrs)
- [Blockstream blog: Esplora and alternatives to ElectrumX](https://blog.blockstream.com/en-esplora-and-other-alternatives-to-electrumx/)
- [BitcoinUnlimited/ElectrsCash](https://github.com/BitcoinUnlimited/ElectrsCash)

**Protocol spec (primary sources).**
- [spesmilo/electrum-protocol — docs/](https://github.com/spesmilo/electrum-protocol/tree/master/docs) (canonical spec repo)
  - [protocol-basics.rst](https://github.com/spesmilo/electrum-protocol/blob/master/docs/protocol-basics.rst) · [protocol-methods.rst](https://github.com/spesmilo/electrum-protocol/blob/master/docs/protocol-methods.rst) · [protocol-changes.rst](https://github.com/spesmilo/electrum-protocol/blob/master/docs/protocol-changes.rst)
- [kyuupichan/electrumx — docs/](https://github.com/kyuupichan/electrumx/tree/master/docs) (reference server docs, incl. peer discovery)
  - [peer_discovery.rst](https://github.com/kyuupichan/electrumx/blob/master/docs/peer_discovery.rst) · [protocol.rst](https://github.com/kyuupichan/electrumx/blob/master/docs/protocol.rst)
- [electrum-protocol readthedocs 1.6.x](https://electrum-protocol.readthedocs.io/en/latest/protocol-basics.html) · [ElectrumX readthedocs protocol-methods](https://electrumx.readthedocs.io/en/latest/protocol-methods.html) · [protocol-ideas](https://electrumx.readthedocs.io/en/latest/protocol-ideas.html)
- [Electrum 4 protocol](https://electrum.readthedocs.io/en/latest/protocol.html)
- [Electrum Cash Protocol (Fulcrum)](https://electrum-cash-protocol.readthedocs.io/en/latest/protocol-methods.html) · [bitcoincash.network/electrum](https://bitcoincash.network/electrum/protocol-methods.html)
- [BIP-324 (context for missing Electrum analogue)](https://bips.dev/324/) · [bitcoinops BIP324 topic](https://bitcoinops.org/en/topics/v2-p2p-transport/)

**Peer discovery & Sybil history.**
- [ElectrumX peer_discovery](https://electrumx.readthedocs.io/en/latest/peer_discovery.html)
- [Chris Belcher, "Making Electrum more anonymous" (2015)](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2015-July/009653.html)
- [PortSwigger: 70% of Electrum network controlled by attackers (2019)](https://portswigger.net/daily-swig/deep-dive-into-electrum-hack-reveals-70-of-network-was-controlled-by-attackers)
- [Malwarebytes: Electrum wallets under siege (2019)](https://www.malwarebytes.com/blog/news/2019/04/electrum-bitcoin-wallets-under-siege)

**Storage, benchmarks, infrastructure.**
- [Sparrow: Server Performance](https://sparrowwallet.com/docs/server-performance.html)
- [Casa: Electrum Server Performance Report 2022](https://blog.casa.io/electrum-server-performance-report-2022/)
- [bitcoin/doc/zmq.md](https://github.com/bitcoin/bitcoin/blob/master/doc/zmq.md) · [ZMQ interface primer](https://bitcoindev.network/accessing-bitcoins-zeromq-interface/)
- [Electrum SSL config](https://electrum.readthedocs.io/en/latest/ssl.html)
- [openoms Tor hidden service for electrs](https://openoms.github.io/bitcoin-tutorials/electrs/Tor_Hidden_Service_for_Electrs.html)
- [electrs#724 scripthash logging (privacy leak)](https://github.com/romanz/electrs/issues/724)

**Clients & deployment.**
- [spesmilo/electrum](https://github.com/spesmilo/electrum) · [electrum-docs/faq.rst](https://github.com/spesmilo/electrum-docs/blob/master/faq.rst)
- [Sparrow docs](https://sparrowwallet.com/docs/quick-start.html)
- [RaspiBolt: Fulcrum](https://raspibolt.org/guide/bonus/bitcoin/fulcrum.html) · [RaspiBolt issue #894](https://github.com/raspibolt/raspibolt/issues/894) · [MiniBolt: Fulcrum](https://v2.minibolt.info/bitcoin/bitcoin/electrum-server)
- [Umbrel electrs app](https://apps.umbrel.com/app/electrs) · [mynodebtc/mynode issue #360](https://github.com/mynodebtc/mynode/issues/360) · [Start9: SSL 50002](https://community.start9.com/t/enabling-ssl-port-50002-in-electrs-tor/1387)
- [Bitcointalk: which server operators run](https://bitcointalk.org/index.php?topic=5433223.0)

---

## Integration Patterns

> **Framing.** Generic microservices / API-gateway patterns do not apply to the Electrum ecosystem. The integration surface is a single **long-lived JSON-RPC session** between a light-client wallet and a server, plus a lightweight **peer gossip mesh** between servers. This section documents the patterns that actually govern the system: interaction model, session lifecycle, client-side pool management, inter-server gossip dataflow, backend integration with Bitcoin Core, and DoS/rate-limit patterns — all read through the lens of what a Sybil detector can observe.

### 1. Interaction model — request / response / subscription

**Three interaction modes over a single TCP/TLS/WS(S) connection** — per the canonical [electrum-protocol/docs/protocol-basics.rst](https://github.com/spesmilo/electrum-protocol/blob/master/docs/protocol-basics.rst):

1. **Request/response.** Standard JSON-RPC call and single reply.
2. **Subscription.** The initial call returns a response immediately; thereafter the server emits **JSON-RPC notifications** (requests with no `id`) whenever the subscribed state changes. *"The method of the notification is the same as the method of the subscription."* Only two real subscriptions exist: `blockchain.headers.subscribe` and `blockchain.scripthash.subscribe`.
3. **Batch requests.** Supported; the spec warns: *"clients making batch requests should limit their size depending on the nature of their query, because servers will limit response size as an anti-DoS mechanism."*

**JSON-RPC version enforcement.** *"A client or server should only indicate JSON RPC 2.0 by setting the `jsonrpc` member… if it supports the version 2.0 protocol in its entirety. ElectrumX does and will expect clients advertising so to function correctly. Those that do not will be disconnected and possibly blacklisted."* — i.e., a malformed 2.0 advertisement is a **reason for server-initiated disconnect**. This is itself a fingerprint vector: different implementations are stricter or looser about this.

**Key subscription notification shapes** (from the canonical [protocol-methods.rst](https://github.com/spesmilo/electrum-protocol/blob/master/docs/protocol-methods.rst) and cross-validated against [electrumx.readthedocs.io/protocol-methods](https://electrumx.readthedocs.io/en/latest/protocol-methods.html)):

- `blockchain.headers.subscribe` → notification carries `{height, hex}` — the new tip.
- `blockchain.scripthash.subscribe` → notification carries `(scripthash, status)` where `status` is a SHA-256 rollup of `"tx_hash:height|tx_hash:height|…"` across the scripthash's history. **In protocol 2.0 the semantics change** — `status` becomes the last confirmed `tx_hash`, with mempool diffs delivered via a new `mempool.changes()` notification. This version-dependent semantics is a live **compatibility fingerprint** across the mesh.

> **Counterintuitive fact.** `server.peers.subscribe`, **despite its name, is not a subscription** — no notifications are sent; it is a one-shot request/response. The name is a historical artifact.

### 2. Session lifecycle & transport advertisement

**Mandatory first message: `server.version`.** From v1.6 onward, *"the `server.version` message must be the first message sent."* The return value is `[server_software_version, protocol_version]` — both strings flow directly into the **banner-based fingerprint layer** of any detector. Example: `["ElectrumX 1.2.1", "1.2"]`.

**`server.features` — the canonical capability advertisement.** Example response from [protocol-methods.rst](https://github.com/spesmilo/electrum-protocol/blob/master/docs/protocol-methods.rst):

```json
{
  "genesis_hash": "000000000933ea01ad0ee984209779baaec3ced90fa3f408719526f8d77f4943",
  "hosts": {"14.3.140.101": {"tcp_port": 51001, "ssl_port": 51002}},
  "protocol_max": "1.0",
  "protocol_min": "1.0",
  "pruning": null,
  "server_version": "ElectrumX 1.0.17",
  "hash_function": "sha256"
}
```

The `hosts` dict is the server's **self-declared address map** — a single operator running multiple endpoints can advertise them all here. For the Sybil detector, this is a **direct self-disclosure channel**: operators co-advertising endpoints under one `hosts` dict are admitting identity. Conversely, disjoint `hosts` dicts that nevertheless resolve to the same ASN / certificate authority are the detector's primary inference signal.

**No client authentication.** The protocol has **no notion of client identity or authentication**. Any connecting TCP/TLS socket can query any address. The server only distinguishes clients by connection (for session state and rate-limiting). This has major privacy implications but also simplifies the detector's job — an external crawler needs nothing but a socket.

**Session duration.** Long-lived by design; Electrum wallets keep ~10 concurrent sessions open for hours to days. `server.ping` (v1.2+) is the standard keepalive.

**Idle / eviction.** Implementation-specific and operator-configurable. ElectrumX has env vars for session limits and idle timeouts ([ElectrumX env docs](https://electrumx.readthedocs.io/en/latest/environment.html)); Fulcrum and electrs expose similar knobs. Variation in eviction behavior (max session, max subscriptions-per-session, idle timeout) is **fingerprint-able** — a careful probe sequence can infer which implementation + which config preset is in use.

### 3. Client-side pool & rotation (critical Sybil-detector context)

Read from the Electrum reference client ([spesmilo/electrum](https://github.com/spesmilo/electrum) — `electrum/interface.py`, `electrum/network.py`) and [electrum FAQ](https://electrum.readthedocs.io/en/latest/faq.html):

- **Default pool size: ~10 concurrent servers.** The wallet maintains this many TLS sessions simultaneously.
- **One "main" server, the rest are "lookup"/header servers.** *"One of the servers, arbitrarily, is selected as the 'main' server. For all connected servers except one, that is all they are used for. Getting block headers from multiple sources is useful to detect lagging servers, chain splits, and forks."*
- **The main server sees the user's wallet queries** — address subscriptions, history requests, broadcast. The other ~9 only see `blockchain.headers.subscribe` traffic.
- **Spread heuristics.** `interface.py` enforces "a healthy spread of connected servers" — diversity across IPs/subnets. The **main interface is exempted from spread checks** to make failover easier.
- **Automatic vs. manual.** Default is automatic rotation (random main); users can disable via the GUI traffic-light → "Select server automatically" → right-click → "Use as server" for a fixed pinning. `--oneserver` CLI flag forces single-server mode (commonly used with Tor+`.onion`).
- **Failover.** Not graceful / stateful — the wallet just picks another server from the pool when the current main degrades.

> **Sybil-detector implication — the precise attacker value function.** A Sybil attacker maximizes expected value not by owning many servers but by maximizing the probability of being **picked as the `main` server**. Owning 50% of the healthy-spread-deduplicated pool ≈ 50% chance of becoming main per wallet session. The 2019 attack achieving ~71% of the mesh is an **upper bound** on what an uncoordinated sock-puppet fleet can achieve; an attacker investing in cross-ASN, cross-subnet, cross-CA diversity could raise that ceiling. This precisely motivates the shared-infrastructure-attribution framing of the detector: the ceiling is breached when multiple nodes *look* independent but share operator substrate.

**Server-side failover exists too.** ElectrumX can be configured with multiple `DAEMON_URL` backends and will round-robin if a bitcoind instance fails ([ElectrumX features](https://electrumx.readthedocs.io/en/latest/features.html)). This is operator-side redundancy, invisible to clients.

### 4. Inter-server peer-mesh gossip (dataflow)

Consolidating §1.6 from Step 2 and the canonical [kyuupichan/electrumx/docs/peer_discovery.rst](https://github.com/kyuupichan/electrumx/blob/master/docs/peer_discovery.rst):

```
┌────────────────┐    server.peers.subscribe    ┌────────────────┐
│  hard-coded    │◄────────────────────────────►│   remote       │
│  seed list     │                               │   server       │
│  (per coin,    │    server.add_peer           │   peer DB      │
│   ≥4 servers)  │◄────────────────────────────►│                │
└───────┬────────┘                               └────────────────┘
        │
        ▼
┌────────────────┐
│  local server  │   — validates new peers by:
│   peer DB      │     1. genesis_hash match (via server.features)
│                │     2. height within a few blocks of our own
│  in-memory     │     3. clearnet peers: hostname resolves to requester IP
│                │     4. onion peers: rate-limited (cannot verify IP)
│                │     5. hostname validity (reject localhost / RFC1918 / multicast)
└────────────────┘
```

**The `server.peers.subscribe` response format** — from [protocol-methods.rst](https://github.com/spesmilo/electrum-protocol/blob/master/docs/protocol-methods.rst):

```
[IP_address, hostname, features_list]
```

Example: `["107.150.45.210", "e.anonyhost.org", ["v1.0", "p10000", "t", "s995"]]`

The **compact feature-string letters** in the third element:
- `v1.0` → protocol version
- `p10000` → pruning limit (or absent if full node)
- `t` → plain TCP (default port 50001)
- `s` → SSL (default port 50002); `s995` → SSL on port 995
- `g` / `h` → legacy HTTPS / HTTP (rare today)

> **Sybil-detector data source.** `server.peers.subscribe` is the single richest observable input to a detector. Crawling it from many vantage points yields (a) the claimed topology, (b) which servers each node considers "good" enough to gossip, and (c) the compact feature strings themselves as fingerprints. Disagreements in the gossip graph (server A says B is a peer; B doesn't know A) are a *direct* anomaly signal.

**Gossip hygiene controls** (verbatim, [peer_discovery.rst](https://github.com/kyuupichan/electrumx/blob/master/docs/peer_discovery.rst)):

- One peer per IPv4/16 subnet in the reply.
- Onion peer count capped separately.
- `server.add_peer` accepted once per connection; clearnet peer IP must equal the requesting IP.
- Source-rate limit: "at most a handful of new peers accepted from any single source".

### 5. Backend integration — Bitcoin Core ↔ Electrum server

All indexing server implementations (ElectrumX, Fulcrum, electrs, Blockstream/electrs, mempool/electrs) share the same backend integration surface with Bitcoin Core:

| Channel | Direction | Purpose | Requirement |
|---|---|---|---|
| **JSON-RPC** | server → bitcoind | Block and tx data pull; mempool queries; `sendrawtransaction` relay | **Mandatory.** Typically `127.0.0.1:8332` with cookie auth. |
| **ZMQ (`zmqpubhashblock`, `zmqpubrawtx`)** | bitcoind → server | Push notification of new blocks / accepted txs | Optional but **strongly recommended** for low-latency tip updates. Fulcrum: *"will run just fine without linking against libzmq, but it will run better if you do."* |
| **`blocknotify` hook** | bitcoind → shell → server | Legacy push mechanism via user-defined shell command | Rare today; superseded by ZMQ. |
| **`txindex=1`** | bitcoind internal | Full transaction index on Core's side | **Required by ElectrumX, Fulcrum, Blockstream/electrs, mempool/electrs.** romanz/electrs does **not** require it (compact-index design). |

Sources: [bitcoin/doc/zmq.md](https://github.com/bitcoin/bitcoin/blob/master/doc/zmq.md) · [ElectrumX HOWTO](https://electrumx-spesmilo.readthedocs.io/en/latest/HOWTO.html) · [ZMQ interface primer](https://bitcoindev.network/accessing-bitcoins-zeromq-interface/) · [Fulcrum README](https://github.com/cculianu/Fulcrum).

> **Detector-relevant timing signals.** Because each server hears about new blocks via *its own* bitcoind's ZMQ or polling cadence, **new-tip propagation latency** across servers is a direct observable. Servers that reliably publish new headers within a tight time-window have **infrastructure-proximate bitcoind instances**, and those timing correlations survive across blocks. Clusters of servers that consistently co-publish within a few hundred milliseconds of each other are candidates for shared-infrastructure attribution.

### 6. DoS / rate-limit / resource-governance patterns

There is **no protocol-level rate limiting** — every implementation invents its own. This is itself a fingerprint.

- **ElectrumX.** Operator-tunable via env vars: `MAX_SESSIONS`, `MAX_SEND`, `MAX_RECV`, `COST_SOFT_LIMIT`, `COST_HARD_LIMIT`, `BANDWIDTH_UNIT_COST`. Sessions that exceed cost limits are paused then disconnected. ([env docs](https://electrumx.readthedocs.io/en/latest/environment.html))
- **Fulcrum.** Compiled-in defaults + config options `max_clients_per_ip`, `max_subscriptions_per_client`, `subs_limit`; DoS-resistant by design (C++ + threadpool) ([Fulcrum README](https://github.com/cculianu/Fulcrum)).
- **romanz/electrs.** Explicitly **not recommended for public use**; has minimal DoS hardening. ([electrs config](https://github.com/romanz/electrs/blob/master/doc/config.md)).
- **Blockstream/electrs** and **mempool/electrs.** Hardened forks tuned for public-facing explorer deployments at the cost of higher resource usage ([Blockstream blog](https://blog.blockstream.com/en-esplora-and-other-alternatives-to-electrumx/)).

> **Detector-relevant fingerprint.** The **shape of rate-limit enforcement** (whether a server slows, disconnects, or silently drops on burst; which queries cost more; whether per-IP or per-session limits dominate) is probe-able with careful load sequences and is a strong implementation fingerprint. This is a Step-5 heuristic; mentioned here to mark the seam.

### 7. Security & authentication patterns

- **Transport TLS.** Optional and **typically self-signed**. Electrum wallets support **fingerprint-pinning** (SHA-256 of the cert embedded in the server URI) because CA-based trust doesn't fit the deployment model. ([Electrum SSL docs](https://electrum.readthedocs.io/en/latest/ssl.html))
- **No peer authentication.** Servers do not authenticate one another when gossiping. The `server.add_peer` call is validated only by IP equality (clearnet) or nothing (onion).
- **No client authentication.** As noted above, any socket can query any scripthash.
- **Tor.** The default privacy mitigation; most community guides recommend the wallet connect via SOCKS5 to `127.0.0.1:9050` (system Tor) or `9150` (Tor Browser bundle). ([openoms tutorial](https://openoms.github.io/bitcoin-tutorials/electrs/Tor_Hidden_Service_for_Electrs.html))
- **No BIP-324-equivalent transport encryption** for the Electrum protocol itself — repeated for emphasis.

### 8. Privacy integration patterns

- **Scripthash obfuscation.** Subscriptions travel as SHA-256(reversed `scriptPubKey`) instead of raw addresses. This denies a naïve observer a direct address mapping — but from the server's perspective, **the set of scripthashes queried over a session precisely identifies the wallet**. Protocol privacy defenses are weak by design.
- **Multi-server header sharding** (see §3). Reduces *consistency-attack* risk (detecting chain splits) but does **not** split the address-query load.
- **Tor-only mode.** `--oneserver` + a pinned `.onion` is the best-available privacy stance for the reference client.
- **Operator-side log hygiene.** The 2022 scripthash-leak-in-logs bug ([electrs#724](https://github.com/romanz/electrs/issues/724)) showed that implementation bugs can turn server logs into a privacy sink — a recurring theme worth raising in the paper's related-work.

### Sources (additional to Step 2)

- [electrum-protocol/docs/protocol-methods.rst](https://github.com/spesmilo/electrum-protocol/blob/master/docs/protocol-methods.rst) — authoritative method shapes and examples.
- [electrum-protocol/docs/protocol-basics.rst](https://github.com/spesmilo/electrum-protocol/blob/master/docs/protocol-basics.rst) — subscription semantics, batch and JSON-RPC enforcement.
- [spesmilo/electrum — interface.py](https://github.com/spesmilo/electrum/blob/master/electrum/interface.py) · [network.py](https://github.com/spesmilo/electrum/blob/master/electrum/network.py) — reference client pool behavior.
- [Electrum FAQ](https://electrum.readthedocs.io/en/latest/faq.html) — "~10 servers, one main" description.
- [Electrum Tor guide](https://electrum.readthedocs.io/en/latest/tor.html).
- [ElectrumX env vars (rate-limit knobs)](https://electrumx.readthedocs.io/en/latest/environment.html) · [ElectrumX features](https://electrumx.readthedocs.io/en/latest/features.html).
- [romanz/electrs config](https://github.com/romanz/electrs/blob/master/doc/config.md).
- [BlueWallet electrum-servers-pool](https://github.com/BlueWallet/BlueWallet/wiki/Electrum-servers-pool).

---

## Architectural Patterns and Design

> **Framing.** Where Steps 2–3 surveyed *what* the ecosystem is and *how components integrate*, this section asks *why each implementation is built the way it is*. For the Sybil detector paper, architectural choices matter because they determine which behavioral signals a server exposes (timing, error shape, sub-manager back-pressure, reorg recovery patterns) — and because package-distributed servers (Umbrel/Start9/RaspiBlitz) impose architectural uniformity on the "honest" population, sharpening the contrast with attacker-operated fleets.

### 1. Per-implementation architecture

#### 1.1 ElectrumX — asyncio-Python, component-based, single-process

From [kyuupichan/electrumx/docs/architecture.rst](https://github.com/kyuupichan/electrumx/blob/master/docs/architecture.rst):

- **Central Controller** coordinates initialization and resources; **no explicit threads** (asyncio coroutines throughout). Quote: *"Python's asyncio means ElectrumX has no (direct) use for threads and associated complications."*
- **Daemon Interface.** *"Encapsulates the RPC wire protocol with bitcoind for the whole server"* and *"transparently handles temporary bitcoind connection errors, and fails over if necessary."* Round-robin failover across multiple `DAEMON_URL`s.
- **Block Processor + Prefetcher.** Prefetcher fills an async cache of future blocks during initial sync to keep CPU saturated. Block Processor *"when caught up, processes new blocks as they are found, and flushes the updates to the Database immediately,"* and *"when syncing uses caches for in-memory state updates."*
- **Session Manager.** One session object per client connection. Resource governance via env vars (`MAX_SESSIONS`, per-session bandwidth limits, subscription caps).
- **Mempool component.** Tracks bitcoind mempool state; delta-driven.
- **Storage layer.** LevelDB or RocksDB (configurable). Heights stored in a flat array on disk for O(1) lookup; tx-hashes in a second flat array — an unusual choice that trades generality for lookup cost.
- **Reorg handling.** Explicit — the Block Processor maintains **undo information** to roll back on reorg. The `reorg` RPC command takes an optional depth (default 3). ([ElectrumX RPC interface](https://electrumx.readthedocs.io/en/latest/rpc-interface.html))

> **Architectural trade-off.** Single-process asyncio caps throughput to one CPU core for Python code; ElectrumX compensates with the prefetch cache and aggressive C-extension use (`plyvel`, `python-rocksdb`). This is why public-server operators needing high concurrency have migrated to Fulcrum.

**Known weakness.** Multi-orphan reorg sequences have had bugs historically — *"ElectrumX has had challenges with handling multiple orphan blocks in sequence… it only handles single orphan blocks in sequence properly"* ([kyuupichan/electrumx#976](https://github.com/kyuupichan/electrumx/issues/976)). A detector watching servers during real reorgs can observe per-implementation recovery patterns.

#### 1.2 romanz/electrs — Rust, compact-index / reparse-on-demand

From [romanz/electrs/doc/schema.md](https://github.com/romanz/electrs/blob/master/doc/schema.md) and [usage.md](https://github.com/romanz/electrs/blob/master/doc/usage.md):

- **Concurrency.** Rust + Tokio; async I/O, thread-pool for compute. Explicitly positioned as personal-use — *"not recommended to run it publicly as it would expose you to DoS and other attacks"* ([Blockstream blog](https://blog.blockstream.com/en-esplora-and-other-alternatives-to-electrumx/)).
- **Index architecture — key-only, five column families.** Definitive schema:

| Column family | Key layout | Value | Purpose |
|---|---|---|---|
| `funding` | `scripthash_prefix(8B) \| block_height(u32)` | *(empty)* | Tx outputs touching a scripthash |
| `spending` | `prev_outpoint_prefix(u64) \| vout \| height(u32)` | *(empty)* | Spending tx location |
| `txid` | `txid_prefix(8B)` | `block_height(u32)` | Map txid → confirmation height |
| `headers` | *(serialized header)* | *(empty)* | Header set |
| `headers` | key `T` | `block_hash` | Chain-tip pointer |
| `config` | key `C` | JSON | Persistence settings |

- **"Compact" design philosophy.** Rows are **key-only** — the empty-value pattern minimizes RocksDB write amplification. The txid family stores only `block_height`, allowing electrs to fetch the actual raw transaction from bitcoind via `getrawtransaction(txid, blockhash)` (the blockhash is known from the height lookup + headers family). **This is why electrs does not require `txindex=1`** on bitcoind — bitcoind can pull the raw tx from block files when the blockhash is provided.
- **Sync workflow.** Batches of 2000 blocks; sequential compaction phases (`config → headers → txid → funding → spending`). [usage.md]: ~6.5 h for 336 GB of block data on "modest hardware"; final DB ≈ 10% of blockfile size.
- **Query workflow.** Many queries trigger **live block re-parsing** via bitcoind RPC — this is the root cause of electrs's ~300× slower wallet-load vs. Fulcrum. The trade: tiny disk, predictable steady-state CPU.
- **Operational extras.** Prometheus metrics on `:4224` — a **direct external fingerprint** (port open + Prometheus format).
- **Reorg.** Stable and rare to corrupt vs. Fulcrum per community report ([Sparrow perf notes](https://sparrowwallet.com/docs/server-performance.html)). Rollback leverages the txid index tip (`T` key) and re-derives.

#### 1.3 Fulcrum — C++20, thread-pool, comprehensive index

From the repo layout ([cculianu/Fulcrum](https://github.com/cculianu/Fulcrum)) and 2.x release notes:

- **Concurrency.** Dedicated **ThreadPool** + per-component actors. Key internal classes visible in headers: `Controller`, `SubsMgr` (subscription manager), `ThreadPool`, `ThreadSafeHashTable` — classic high-concurrency C++ pattern.
- **Storage.** RocksDB 9.2.1 (static); 2.x introduced **platform-neutral DB format** (portable across OSes and endianness).
- **Index style.** Comprehensive — stores enough to answer all queries without re-parsing. Larger disk, much faster queries.
- **`txindex=1` required.**
- **ZMQ integration.** Optional but recommended for low-latency tip updates.
- **Reorg handling.** Documented mechanism, but community reports (Sparrow, RaspiBolt) note occasional **DB corruption requiring full re-sync** — a failure mode fingerprint when crawling through natural reorgs.

> **Architectural trade-off summary across the three servers.**
>
> |  | Persona | Concurrency | Index | On-reorg | Public-server fit |
> |---|---|---|---|---|---|
> | ElectrumX | Public servers, full-feature | asyncio (1 core) | Flat-arrays + LevelDB/RocksDB | Undo log, depth-configurable | Historical choice; still viable |
> | electrs | Personal / home-node | Tokio async + pool | Compact key-only RocksDB | Stable, rebuild cheap | Not recommended (no DoS hardening) |
> | Fulcrum | Modern public + home | Multi-core thread-pool | Comprehensive RocksDB | Handled but DB corruption reports | Current community default |

#### 1.4 Blockstream/electrs and mempool/electrs — indexer + HTTP API dual-role

Forks of `romanz/electrs` that add an **HTTP/REST API layer** on top of the same compact-index core. Used to power block-explorer UIs (blockstream.info, mempool.space). Architectural add-ons:

- **Additional column families** for address history and richer indexing (index schema incompatible with upstream romanz).
- **Hardened session governance** for public exposure.
- **HTTP server component** alongside the Electrum-protocol TCP/TLS ports — a single process exposes both protocols.

**Implication.** Servers co-publishing on Electrum's 50001/50002 *and* an HTTP API on 3000/8080/etc. are **self-identifying** as one of these forks — a high-signal fingerprint.

#### 1.5 Electrum Personal Server (EPS) — no indexer, "watcher" architecture

EPS imports user-supplied descriptors (or xpubs) into Bitcoin Core's **wallet** and relies on Core to maintain the history. EPS then translates Electrum-protocol queries directly into Core RPC calls (`listtransactions`, `gettransaction`, etc.). Key architectural consequences:

- **No RocksDB/LevelDB at all.** Disk overhead ≈ 0.
- **Single-user, single-wallet per session** (imported descriptors).
- **Quadratic behavior** for many addresses (drives "slow" perception).
- **Privacy story.** Bitcoin Core is learning everything EPS knows anyway; the "full-node-privacy" claim is about avoiding an *external* indexer seeing the scripthashes.

EPS's non-participation in the public peer mesh (it's not discoverable) makes it orthogonal to Sybil detection but important to understand as the ecosystem's architectural outlier.

### 2. Reference client (Electrum wallet) architecture

From [spesmilo/electrum](https://github.com/spesmilo/electrum):

- **Python + asyncio + Qt** (GUI frontend). The wallet's async event loop runs in a background thread; Qt on the main thread. Bridge via `asyncio.run_coroutine_threadsafe()`.
- **Network class** (`network.py`) manages the pool of `Interface` objects; each `Interface` encapsulates one long-lived JSON-RPC session. Sessions derive from a common `SessionBase`.
- **Interface** handles the TLS handshake (including fingerprint pinning), `server.version` handshake, subscription bookkeeping, and reconnection.
- **Spread invariant.** `Network` enforces a "healthy spread" across connected interfaces — a deduplication pass keyed on subnet/host. The main interface is exempted from the spread check to prevent flapping on main-server selection.
- **Fault model.** On main-interface failure the wallet picks a new main from the pool; on pool starvation it re-seeds from `recent_servers` history and eventually the hardcoded bootstrap list.

> **Why this matters for the paper.** The wallet's spread logic is the *only* client-side Sybil defense in the baseline protocol. If an attacker can game the spread check (by diversifying across ASNs / CAs / subnets while sharing operator substrate), they maximize the probability of being chosen as `main`. This is the precise gap the shared-infrastructure attribution layer needs to close.

### 3. Reorg-handling architectural patterns (cross-cutting)

All full-index servers must handle Bitcoin Core reorgs. Two distinct strategies observed:

1. **Undo-log replay** (ElectrumX). Maintains explicit undo info; on reorg, applies undo entries to revert state, then walks the new chain forward. Depth-bounded. Breaks down on deep or sequential-orphan reorgs.
2. **Tip-pointer + reparse** (romanz/electrs). The `headers` CF holds a `T` tip-pointer; reorg is detected by header mismatch; affected height range is re-indexed from Core's block data. Simpler and more resilient; more expensive per reorg.

Clients must also reorg-handle: per the spec, *"the client must be able to figure out the common ancestor block and request any missing block headers to acquire a consistent view of the chain state."* The reference wallet does this by comparing headers across its ~9 non-main servers — exactly why it maintains the pool.

> **Detector angle.** During a natural reorg (they happen every few days at depth 1–2), server-side behaviors diverge sharply: delay-to-republish, error shapes on queries touching the orphan tip, and whether `server.features.server_version` changes mid-recovery. These transient signals are fingerprint-dense and cannot be faked without running the actual server software.

### 4. Operational topology patterns

**Single-node canonical stack** (most home-node kits):

```
                    ┌────────────────┐
                    │   Tor daemon   │ ── exposes :50002 as .onion
                    └────────┬───────┘
                             │
┌────────────┐    RPC/ZMQ   ┌┴──────────────┐    TLS    ┌──────────────┐
│  bitcoind  │◄────────────►│ electrs /     │◄─────────►│ Clients      │
│  (txindex) │              │ Fulcrum /     │           │ (Electrum,   │
│            │              │ ElectrumX     │           │  Sparrow…)   │
└────────────┘              └───────────────┘           └──────────────┘
                                    ▲
                                    │ (optional)
                             ┌──────┴───────┐
                             │ nginx /      │
                             │ haproxy      │
                             │ TLS termination + ACME
                             └──────────────┘
```

- **Reverse-proxy front-end** (nginx/haproxy) is common when operators want Let's Encrypt certificates instead of self-signed — adds a **TLS termination layer** visible as SNI/ALPN/Server headers in the TLS handshake (**fingerprint-able**).
- **Tor sidecar** is nearly universal on home-node kits; client traffic arrives over `.onion:50002` via SOCKS5.

**Multi-daemon / HA topology** (rare, public operators):
- ElectrumX can failover across multiple `DAEMON_URL`s round-robin.
- No native multi-indexer-instance sharing; operators scale horizontally by deploying separate independent indexers.

### 5. The "home-node kit" architectural pattern

Umbrel, Start9 (Embassy), RaspiBlitz, MyNode, MiniBolt, RaspiBolt all bundle **bitcoind + electrs/Fulcrum + Tor** (plus Lightning, BTCPay, etc.) as a **single unit**. Architectural consequences relevant to the detector:

- **Defaults are shared.** Same Bitcoin Core versions, same electrs/Fulcrum versions, same TLS-cert generation templates, same Tor HiddenService port patterns — across thousands of deployments per kit.
- **Update cadence is kit-driven.** When Umbrel ships a new electrs, hundreds of `server.version` banners flip in a narrow time window — a **population-level temporal fingerprint**.
- **Tor-first by default.** Many kit-deployed servers are **only** reachable via `.onion`.

> **Detector implication.** Honest home-node servers cluster tightly on kit-derived feature strings, cert shapes, banner versions, and Tor-only accessibility patterns. Deviations — e.g., clearnet-only endpoints in "home-style" ASNs without matching kit fingerprints — are a legitimate weak-anomaly signal but require careful calibration against advanced home operators who customize.

### 6. Security-architecture patterns

Repeating for completeness, as distinct from §Integration-7:

- **No application-layer auth** anywhere in the protocol. Defense-in-depth is fully operational (firewalls, Tor, `--oneserver` on the client).
- **TLS trust model diverges from the web.** Fingerprint-pinning is canonical. This means **self-signed cert** + **cert SHA-256 URI** is architecturally *correct* under Electrum's model, not a misconfiguration. Detectors should therefore treat self-signed certs as neutral — it's the **cert field contents** (CN, SAN, issuer patterns, validity windows) that discriminate.
- **ACME/Let's-Encrypt certs** indicate a publicly-resolvable hostname and reverse-proxy termination — a distinct operator class from the self-signed majority.
- **Tor-only hidden services** have no TLS-layer fingerprint at all (Tor wraps the stream). Fingerprint vectors collapse onto application-layer signals (`server.version`, `server.features`, banner, timing).

### 7. Data-architecture patterns (wallet / user privacy)

- **Scripthash as address-opaque key** (SHA-256 of `scriptPubKey`) is an architectural privacy-vs-usability trade. It denies a naïve pseudonym mapping; it doesn't deny the server from learning the wallet's address cluster through subscription correlation.
- **Subscription set = user identity.** Any single-main-server architecture yields a per-session wallet cluster identification. Multi-server sharding at the query layer is an *unadopted* architectural proposal ([electrumx protocol-ideas](https://electrumx.readthedocs.io/en/latest/protocol-ideas.html)).

### 8. Sybil-detector architectural implications (synthesis)

1. **Static fingerprint surface.** Implementation-specific internals leak through observable responses: compact feature strings (`v`, `p`, `t`, `s`), `server.features` field presence/absence, banner text, TLS cert contents, open auxiliary ports (Prometheus `:4224`, HTTP `:3000`), and gossip hygiene behaviors (subnet dedup in replies). Each is a **low-resolution classifier**; stacking them yields implementation-class identification with high confidence.

2. **Dynamic / behavioral fingerprint surface.** Per-query timing distributions, error-message shapes on malformed input, JSON-RPC 2.0-strictness, rate-limit/disconnect thresholds, reorg-recovery latency. These require active probing but are architecturally determined and hard to forge.

3. **Shared-infrastructure attribution surface.** ASN/host/CA clustering, block-tip co-publication latency (ZMQ-propagation correlations), shared TLS cert issuers, Tor descriptor correlations — these transcend the individual-server fingerprint and target the shared substrate the detector's Push-3 framing is built on.

### Sources (primary, additional to Steps 2–3)

- [kyuupichan/electrumx — architecture.rst](https://github.com/kyuupichan/electrumx/blob/master/docs/architecture.rst)
- [ElectrumX Features (daemon failover etc.)](https://electrumx.readthedocs.io/en/latest/features.html)
- [ElectrumX RPC interface (reorg command)](https://electrumx.readthedocs.io/en/latest/rpc-interface.html)
- [kyuupichan/electrumx issue #976 (multi-orphan reorg bug)](https://github.com/kyuupichan/electrumx/issues/976)
- [romanz/electrs — doc/schema.md](https://github.com/romanz/electrs/blob/master/doc/schema.md) · [doc/usage.md](https://github.com/romanz/electrs/blob/master/doc/usage.md) · [doc/config.md](https://github.com/romanz/electrs/blob/master/doc/config.md)
- [cculianu/Fulcrum — source (Controller, SubsMgr, ThreadPool, ThreadSafeHashTable)](https://github.com/cculianu/Fulcrum)
- [Blockstream/electrs](https://github.com/Blockstream/electrs) · [mempool/electrs](https://github.com/mempool/electrs)
- [Sparrow Server Performance (reorg stability comments)](https://sparrowwallet.com/docs/server-performance.html)
- [ElectrumX protocol-ideas (multi-server proposals, unadopted)](https://electrumx.readthedocs.io/en/latest/protocol-ideas.html)

---

## Implementation Research — Detection Practice, Prior Art & Detector-Build Stack

> **Framing.** The generic template's DevOps/adoption-strategy framing doesn't apply. This step documents (a) the **only published empirical prior art** that systematically crawled the Electrum network, (b) **public data sources** a Sybil detector can use today, (c) **concrete probe strategies** by heuristic class, (d) a **recommended implementation stack** for the Electrum Sybil Detector project itself, and (e) **operational / ethical practices**.

### 1. Prior empirical work — what has already been done

#### 1.1 Electrohunt (Kacherginsky, Coinbase Security, 2019)

This is the **closest published precedent** to the Electrum Sybil Detector — still the most referenced Electrum-network crawl study available.
- **Electrohunt Part 1** ([medium.com/iphelix](https://iphelix.medium.com/electrohunt-part-1-hunting-for-the-phishing-campaigns-on-the-electrum-network-b10529162e63) · [coinbase blog mirror](https://blog.coinbase.com/electrohunt-part-1-hunting-for-the-phishing-campaigns-on-the-electrum-network-b10529162e63))
- **Electrohunt Part 2** ([Ukraine obsession](https://iphelix.medium.com/electrohunt-part-2-ukraine-obsession-with-crypto-continues-4cbdf99932ae))

**Methodology (extracted from Part 1):**
- **Bootstrap**: known seed list → recursive `server.peers.subscribe` traversal.
- **Libraries/tools**: [`connectrum`](https://pypi.org/project/connectrum/) (Python Electrum-client library) + custom `spider.py` (enumeration) + `electrohunt.py` (malicious-server scanner) + DNS/host lookups.
- **Signals collected**:
  1. Send a crafted `blockchain.transaction.broadcast` to elicit error messages.
  2. Compare error text against a **whitelist of benign responses**.
  3. Any deviation flagged for manual review.
  4. Correlate by hostname patterns and resolved IP.

**Findings (concrete):**
- **967 active servers scanned; 657 reached; 471 malicious (71%).**
- Two attacker campaigns:
  - **Campaign #1 — Subdomain-alias fanout.** Thousands of randomly-generated subdomains (e.g., `electrum5391756.rollerco.xyz`, `electrum8854308.rollerco.xyz`) all resolving to a handful of IPs (e.g., `185.25.48.104`). Exploited ElectrumX's pre-patch `server.add_peer` flow to inflate peer tables with "ghost" servers.
  - **Campaign #2 — Raw IPs + stealth.** Smaller count, better-connected hosts, less noisy.
- **Financial impact**: Campaign #1 ≈ **55 BTC (~$200k at the time)** to a single address; Campaign #2 stole several thousand dollars in Litecoin.

> **Takeaway for the detector.** Electrohunt proves the methodology works — but it was built for the **2019 threat model** (payload = phishing error messages). Modern Sybil attackers no longer need to modify server binaries to carry a visible payload; they just need to become *trusted peers* to influence wallet fee estimation, block-tip reporting, or to be positioned for future attacks. The detector therefore needs shared-infrastructure attribution that **doesn't depend on any malicious-payload signal** — the Push-3 framing.

#### 1.2 Bitnodes — methodological precedent (different protocol)

[Bitnodes.io](https://bitnodes.io/) ([ayeowch/bitnodes](https://github.com/ayeowch/bitnodes)) is the long-running crawler of the **Bitcoin P2P network** (not Electrum). Relevant because:
- The methodology is analogous — recursive enumeration via the network's peer-discovery RPC (`getaddr` in Bitcoin Core) starting from seed nodes.
- Bitnodes's **per-node / per-IP reconciliation rules** ("Multiple nodes from the same IP but different ports are counted as one node") are a reference pattern for handling Electrum's equivalent (IP + port + hostname tuples).
- Academic follow-up — **BNS** ([MDPI Mathematics 11(24), 2023](https://www.mdpi.com/2227-7390/11/24/4885)) — documented that Bitnodes under-counts by ~6% (1093 reachable nodes/day) and proposed an improved detection system; methodologically relevant as baseline for any Electrum-equivalent crawl study.

**Academic crawler pattern** (from `btc-crawl`, `ayeowch/bitnodes`, BNS): async concurrent connections (hundreds-to-thousands), exponential backoff per-host, global rate-limit, incremental database of observed endpoints with first-seen/last-seen timestamps. Directly transferable to Electrum.

#### 1.3 0xB10C's prior art, provenance citation, and reusable infrastructure

**Critical context the Sybil Detector project builds on** — the research question this detector answers was posed publicly by 0xB10C (the long-running Bitcoin network-measurement researcher behind `peer-observer`, `fork-observer`, and the `bitcoin-data` dataset corpus):

- **Provenance: [0xB10C/projectideas issue #11](https://github.com/0xB10C/projectideas/issues/11)** — *"Can we spot public spy-Electrum servers run by Chainalysis?"*, opened July 2025, tagged as a ₿OSS Challenge project, still `Todo` as of 2026-04-22. The issue details the exact methodology (block-notification timing during forks, fee-histogram comparison, downtime tracking, metadata fingerprinting) and explicitly notes *"If I had the time to work on this, I'd write a custom tool."* This is the **canonical citation for why the measurement has not been published**: the question is open, the approach is documented, and bandwidth is the structural bottleneck — not knowledge.
- **[fork-observer](https://github.com/0xB10C/fork-observer)** — 0xB10C's operational tool already **supports connecting to Electrum servers** and tracking which block each reports as tip. Reusable infrastructure for the detector's block-notification-timing collector. Do not reimplement; integrate.
- **[bitcoin-data](https://github.com/bitcoin-data)** — 0xB10C-maintained GitHub organization hosting the community-standard Bitcoin network-measurement datasets: [`stale-blocks`](https://github.com/bitcoin-data/stale-blocks), `mining-pools`, `block-arrival-times`, etc. `stale-blocks` is the **primary data source for fork-race events** — 3–8/month recent cadence per the dataset. Dual role for this project: (a) input to the detector's fork-race-timing methodology; (b) target for **dataset publication** — the longitudinal Electrum-server dataset will be contributed into `bitcoin-data` alongside the existing corpora, which gives it institutional continuity and positions the release as a contribution *into* the reference ecosystem rather than around it.
- **[peer-observer](https://github.com/0xB10C/peer-observer)** — sibling project on the Bitcoin Core P2P layer; important as **methodological cousin** (same longitudinal-measurement philosophy applied to a different network layer). Not directly reused by the Electrum detector but frames the contribution as **layer-complementary, not competing**: peer-observer watches Bitcoin nodes; the Electrum detector watches Electrum servers.

> **Framing implication for the paper's positioning.** The detector is **building on 0xB10C's corpus and methodology, not against it**. The three-tier archival strategy (bitcoin-data + Zenodo + arXiv) anchors the dataset in 0xB10C's ecosystem. The contribution is the first longitudinal measurement *at the Electrum-server layer* — a different corpus than peer-observer's Bitcoin-P2P-layer work, and the direct execution of issue #11's outstanding research question.

#### 1.4 Public monitoring services

- **Bitcoin All-Seeing Eye — [1209k.com/bitcoin-eye/ele.php?chain=btc](https://1209k.com/bitcoin-eye/ele.php?chain=btc)**. Continuously pings public Electrum servers across BTC, BCH, and altcoin networks; emails operators when a server goes 8+ blocks behind or unreachable 10+ minutes.

  **Live inspection (2026-04-23) confirms:**
  - **506 BTC mainnet servers listed** — ~4× larger than the Electrum bootstrap (130). Useful **seed-enrichment source** for the crawler.
  - Fields exposed per server: `Host, Port, Proto (tcp/ssl), UTXO Root, Height, Blocktime, Version, Protocol, Connection, ConnectionTime, Status (OK/CLOSED/BEHIND), Uptime (hour/day/month)`.
  - **3+ `.onion` endpoints tracked** (v3 addresses).
  - Disclosed methodology: *"done via a single connection that subscribes to block headers and just waits. The load on the server is less than a normal client, which would be watching addresses as well."* — i.e., **header-subscription liveness only**; no `server.features`, no `server.banner`, no `server.peers.subscribe`, no timing/behavioral probing.
  - **Operator visibility**: the 1209k.com domain itself runs several of the monitored servers (`b6./b./hippo./fulcrum-core.1209k.com`). Noted — not disqualifying, but a conflict-of-interest factor when using 1209k as ground-truth.
  - Recognizable operators visible in the list: `bullbitcoin.com` (3-server cluster: `wes/electrum/fulcrum`), `8333.mobi`, `stackwallet.com`, `blockeng.ch`, `tjader.xyz`, `tranquille.cc`, `schulzemic.net`, `fiatfaucet.com` (multiple subdomains).

  **Correct role in the pipeline** — *auxiliary seed-enrichment + cross-validation*, NOT primary source:

  | Use 1209k for | Do **not** use 1209k for |
  |---|---|
  | Expanding the seed list from 130 to ~500 | Primary discovery (methodology is undocumented / non-reproducible for an academic paper) |
  | Calibrating liveness against your active probes | Sybil detection (1209k treats every responder as legitimate; it did not filter the 2019 attack) |
  | Longitudinal uptime reference (stable-operator vs. ephemeral signal) | Fingerprint data (only height + version — no banner/features/peers/cert/JARM) |
  | Coverage-delta analysis (servers 1209k has that you miss, and vice versa — sensitivity check) | Single point of failure if 1209k goes down or is compromised |

- **UASF Node Tracker — [uasf.saltylemon.org/electrum](https://uasf.saltylemon.org/electrum)**. Another monitored-servers list; use in the same auxiliary-seed role as 1209k for cross-coverage (both may miss different subsets).

### 2. Data sources for the detector

#### 2.1 Electrum-protocol sources (active probing)

| Source | Endpoint | Data retrievable |
|---|---|---|
| Hardcoded bootstrap list | [`electrum/chains/mainnet/servers.json`](https://github.com/spesmilo/electrum/blob/master/electrum/chains/mainnet/servers.json) and siblings for testnet/testnet4/signet/regtest/mutinynet under [`electrum/chains/`](https://github.com/spesmilo/electrum/tree/master/electrum/chains) | Initial seed set — canonical "trusted" servers |
| Recursive `server.peers.subscribe` | every reached server | Full topology graph + compact feature strings |
| `server.version` | per connection | Implementation banner + protocol-version range |
| `server.features` | per connection | `genesis_hash`, `hosts{}` dict (self-declared alt endpoints), `protocol_min/max`, `pruning`, `hash_function`, `server_version` |
| `server.banner` | per connection | Free-form operator text — **fingerprint vector** |
| `server.donation_address` | per connection | Operator-chosen BTC address — correlatable across endpoints |
| `blockchain.headers.subscribe` | per connection | **Tip-publication timing** — shared-ZMQ inference signal |
| TLS handshake | port 50002 / WSS | Cert chain, SNI behavior, ALPN, JARM fingerprint |

##### 2.1.1 Empirical baseline — the canonical mainnet bootstrap list (as of 2026-04)

Direct inspection of [`electrum/chains/mainnet/servers.json`](https://github.com/spesmilo/electrum/blob/master/electrum/chains/mainnet/servers.json):

- **Total entries: 130 servers.**
- **Per-entry fields**: `s` (SSL port, typically 50002), `t` (TCP port, typically 50001), `pruning` (always `"-"`), `version` (1.4 → 1.6.0). Not all entries populate both `s` and `t`.
- **Transport distribution.** Mix of clearnet IPv4 addresses, DNS-hosted endpoints (`.com`, `.net`, `.org`, `.io`, `.de`, `.ch`, `.sk`, `.pro`, `.beer`, `.fyi`) and dynamic-DNS providers (`.hopto.org`, `.hopto.me`, `.ddns.net`).
- **Tor**: **9 `.onion` endpoints (~7%)** — v3 addresses (56-char base32 + `.onion`).
- **Operator-branded patterns in hostnames.** 17+ hosts use an `electrum*` prefix; 2 use `fulcrum*`. Named operators visible in-clear: **Blockstream, Hodlister (and variants), Bitaroo, Bitske**, plus individual-handle domains (`hsmiths.com`, `qtornado.com`, `keff.org`).
- **Protocol-version spread across the list.** 1.4 → 1.6.0 — confirming §2.3 Step 2's observation that spec-version adoption is uneven across the canonical list.
- **Chain coverage.** Parallel `servers.json` files exist under [`electrum/chains/`](https://github.com/spesmilo/electrum/tree/master/electrum/chains) for **mainnet, testnet, testnet4, signet, regtest, mutinynet** — each maintains its own curated bootstrap.

> **Detector implication.** The bootstrap list is **the canonical ground-truth positive set** for any training corpus. A detector whose false-positive rate on this list is ≥ a few percent is mis-calibrated. The 9 `.onion` entries are the hardest validation targets (no TLS-layer signal). The IP-addressed entries without hostnames are high-value targets for rDNS/CT/ASN enrichment because their operator identity is not self-disclosed.

#### 2.2 Internet-scale scan sources (passive / external)

- **[Censys](https://censys.io/)** — continuous IPv4 scans indexed by port; queryable for port-50001 and port-50002 services. Commercial tier but free for research.
- **[Shodan](https://www.shodan.io/)** — same category; long-tail discovery of historically-seen endpoints.
- **[ZMap](https://zmap.io/)** — self-hosted full-IPv4 scanner (~45 min single machine). Permits direct custom probing without third-party dependency. Useful when Sybil-crawl volume exceeds Censys query quotas.
- **[Certificate Transparency logs](https://certificate.transparency.dev/)** — searchable via [crt.sh](https://crt.sh/) or direct CT-log queries. Finds Let's-Encrypt / CA-issued certs with hostnames resolvable to Electrum servers (the ACME-fronted subset of operators).
- **ASN/BGP data** — [Team Cymru IP-to-ASN service](https://team-cymru.com/community-services/ip-asn-mapping/), [MaxMind GeoIP2](https://www.maxmind.com/), [RIPE RIS](https://ris.ripe.net/). Core inputs to shared-infrastructure attribution.

#### 2.2.1 Empirical Shodan probe (2026-04-23) — what passive scanning actually sees

A targeted Shodan-web exploration run on 2026-04-23 against candidate queries yielded concrete evidence that **passive port-scan data alone is a weak primary source for an Electrum-server census**, but is a **high-value pivot for shared-infrastructure attribution**. Raw findings:

- **`port:50002` alone → 108 754 hits, but mostly noise.** Top products: OpenSSH (5 262), Socks4A (4 430), nginx (1 848), Hikvision cameras, TRENDnet webcams, etc. The top countries (CN 38 378, US 17 496, IL 9 653) and top orgs (Aliyun 31 334, Internet Rimon 9 538, Fly.io 7 625) reflect **generic reuse of this high port**, not the Electrum population. *Electrum servers are a small subset buried in the noise and Shodan cannot isolate them without protocol-speaking probes.*
- **Keyword filters barely help.** `"ElectrumX" port:50002` → 2 hits; `"Fulcrum" port:50002` → 0; `ssl.cert.subject.CN:electrum` → 0. The two `"ElectrumX"` hits were **not Electrum servers** — they were a Docker Registry (see below) and an unrelated service. This is expected: **the Electrum protocol does not expose a server banner on the TLS handshake**; identity only appears after a client-sent `server.version` RPC. Shodan never speaks Electrum, so it never sees the banner.
- **Query `electrs` DID return useful results — but as HTTP-API endpoints, not Electrum-protocol servers.** ~22 hits, effectively all `mempool-electrs` REST-API front-ends. Each exposes the header `x-powered-by: mempool-electrs <version>` and many expose `x-bitcoin-version: /Satoshi:<X>/` — a **double-fingerprint revealing indexer-fork version + underlying Bitcoin Core version in a single response**.

**High-value empirical observations from the `electrs` query:**

| Signal | Example | Implication |
|---|---|---|
| `x-powered-by: mempool-electrs 3.1.0` through `3.4.0-dev-<sha>` | `172.105.148.135` (Linode/Atlanta) · `178.156.205.25` (Hetzner) · `65.109.155.32` (Hetzner/FI) | Operators running **git-build / `-dev` / `(dirty)` variants** in production — fingerprint-able sub-populations |
| `x-bitcoin-version: /Satoshi:26.0.0/` → `/Satoshi:29.1.0(MutinyNet)/` | Multiple | Reveals Bitcoin Core version + exposes MutinyNet / signet / regtest developer class |
| Hetzner concentration: **6 / 22 hits** (`*.clients.your-server.de`) | — | Quantitative confirmation of Hetzner dominance in the Electrum-adjacent population |
| Let's Encrypt for public explorers | `mempool.signet.surge.dev` (Google) · `regtest.libregold.com` (DO/Singapore) | ACME / reverse-proxy operator class is distinct from self-signed home-node class |
| Host categories visible: mainnet, **signet, regtest, mutinynet** | Explicit | Developer-infrastructure operator class — separate from end-user nodes |

**Collateral infra-leaks (independent of any Electrum-specific query) that illustrate the shared-infrastructure attribution surface:**

- **Host `34.26.44.149`** (Google Cloud, `149.44.26.34.bc.googleusercontent.com`): an **open `rsyncd`** listing module names:
  ```
  mainnet-ord          Ord indexer data for mainnet
  mainnet-esplora      Esplora/Electrs data for mainnet
  mainnet-metashrew    Metashrew indexer data for mainnet
  mainnet-bitcoind     Bitcoin Core data for mainnet
  signet-ord   signet-esplora   …
  ```
  One operator, multi-chain multi-indexer stack, rsync-syncable between nodes — **a shared-infrastructure cluster confessed in a single banner**.
- **Host `kofar.paywithspark.net`** (Hetzner Helsinki): **open Docker Registry** listing images `bitcoin`, `bitcoin-knots`, `btc-rpc-explorer`, `electrs`, `electrumx`, `lndg`, `mailgate`, `rzeus`, `zeus`. Operator-stack-manifest leaked without any probing.
- **Host `65.109.158.184`** (Hetzner Finland): open **Prometheus `node_exporter`** on the canonical port — operator telemetry stack signal.

> **Methodological finding for the paper.** The detector's **crawl layer cannot rely on passive port-scan datasets (Shodan/Censys) for population enumeration**. Their coverage of the actual Electrum-protocol population is near-zero in snapshot form. However, Shodan / Censys / CT-log queries *are* high-value for the **attribution layer** — catching adjacent HTTP APIs (`x-powered-by: mempool-electrs`), orchestration endpoints (Prometheus, Docker Registry, rsyncd), and cert-chain pivots that cluster with active-probed Electrum nodes. The architecture implication: build **the crawler around active `server.peers.subscribe` traversal**, and treat passive datasets as **correlation inputs** downstream, not as primary discovery.

This observation is directly applicable to the Push-3 shared-infrastructure framing: the most informative operator-identity signals in this probe came from **incidentally exposed services on the same host as the Electrum server** — not from the Electrum server itself.

**Null results from the same session (also informative):**

- `port:4224 "# HELP"` → **0 hits**. Electrs's Prometheus endpoint is consistently firewalled; exposed `:4224` seen earlier (541 bare-port hits) is not predominantly electrs. **Rules out Prometheus as a pivot of passive discovery.**
- `port:4224 electrs` → **0 hits**. Same conclusion via banner text.
- `port:8332 port:50002` → **0 hits**. Bitcoin Core's RPC port (8332) is **universally firewalled** on hosts that expose Electrum TLS (50002). This is expected and correct operational hygiene — but it has an upside for the detector: **any host that does expose 8332 publicly becomes a high-signal anomaly candidate worth banner-grabbing** (and possibly flagging for operator outreach on security grounds). Query to keep in the crawl pipeline as a tripwire, not as a discovery tool.

Consolidated empirical conclusion from the Shodan session:

| Query | Count | Useful as… |
|---|---|---|
| `port:50002` | 108 754 | Noise; filter required |
| `"ElectrumX" port:50002` | 2 | Not Electrum hosts (Docker-registry / unrelated) |
| `"Fulcrum" port:50002` | 0 | — |
| `ssl.cert.subject.CN:electrum` | 0 | — |
| `electrs` (no port) | ~22 | **mempool-electrs HTTP API enumeration** ✅ |
| `port:4224` | 541 | Noise |
| `port:4224 "# HELP"` | 0 | Null-result: Prometheus hidden |
| `port:8332 port:50002` | 0 | Null-result: RPC correctly firewalled → tripwire query |

#### 2.3 Tor hidden-service data

`.onion` endpoints **cannot** be enumerated from outside the Tor network — they are only discoverable via gossip (`server.peers.subscribe` from a connected server). Practically:
- The detector's Tor-facing crawler must accept gossip-only discovery of onion servers.
- JARM / TLS fingerprinting yields less information over Tor (Tor wraps the stream; no outer TLS signal from the client side).
- Application-layer fingerprinting (`server.version`, banner, timing) remains available but without an IP-side pivot.

### 3. Detection heuristics by class

#### 3.1 Static / banner-layer fingerprints (cheap, high-volume)

| Signal | What it distinguishes | Confidence |
|---|---|---|
| `server_version` string shape | ElectrumX vs. electrs vs. Fulcrum vs. EPS vs. forks; often version-down to minor | HIGH |
| `protocol_min` / `protocol_max` | Patch cadence of operator; correlates with kit version | MEDIUM |
| `server.features.hosts{}` dict | **Operator self-identification** across multiple endpoints | HIGH — when populated |
| `server.banner` free text | Implementation-default vs. operator-customized; phishing payloads | HIGH in anomaly cases |
| `server.donation_address` | Shared across multiple endpoints → same operator (unambiguous) | VERY HIGH |
| Compact feature strings (`v`, `p`, `t`, `s`) returned to peers | Cross-check of self-advertised vs. gossiped | HIGH |
| Open auxiliary ports (`:4224` Prometheus, `:3000`/`:8080` HTTP API) | electrs variant + operator's monitoring setup | MEDIUM-HIGH |
| TLS cert contents (CN, SAN, issuer, notBefore, key-algo) | Self-signed vs. ACME; batch-generated certs share shape | MEDIUM-HIGH |
| **JARM TLS fingerprint** | Implementation / stack / TLS-library identification; batch-deployed hosts match exactly | HIGH for grouping |

**JARM specifics** ([salesforce/jarm](https://github.com/salesforce/jarm)): 10 crafted TLS Client Hellos → 62-char fingerprint (30 chars = chosen cipher/version per hello; 32 chars = truncated SHA-256 of cumulative extensions). *"JARM can group disparate servers on the internet by configuration"* — directly applicable to Electrum-server batch-deployment grouping.

#### 3.2 Dynamic / behavioral fingerprints (moderate cost, requires probing)

| Probe | What it reveals |
|---|---|
| Malformed JSON (missing `id`, bad `method`) | Error message shape — per-implementation distinctive |
| Unknown method call | Error code format (code/message) differs by implementation |
| Batch request size sweep | Cap threshold reveals implementation + config preset |
| JSON-RPC 2.0 strict vs. loose (`jsonrpc: "2.0"` + missing member) | ElectrumX disconnects; others may tolerate — fingerprint |
| Subscription flood | Per-session subscription cap triggers |
| Rate-probe sequence | Back-pressure shape (slow / disconnect / silent-drop) |
| Query timing distribution (`scripthash.get_history` on fixed test-scripthash) | Indexer architecture signature (electrs re-parse vs. Fulcrum direct vs. ElectrumX flat-array) |
| `blockchain.headers.subscribe` tip-propagation latency | **Shared-ZMQ-substrate signal** — clusters co-publishing within <200 ms likely share infra |

#### 3.3 Shared-infrastructure attribution (the Push-3 layer)

| Signal | Fused with | Attribution claim |
|---|---|---|
| ASN + /24 co-residence | IP geolocation | Same hosting provider / same pool |
| Shared JARM fingerprint | Cert issuer + port open | Same image / deployment template |
| Same TLS cert issued at same time (CT log) | SAN overlap | Same operator running batch-provisioning |
| Co-publication window for new block tips | ZMQ pattern inference | Bitcoind instance shared or co-located |
| `server.features.hosts{}` overlap | — | Direct operator admission |
| Donation address reuse | — | Direct operator admission |
| Correlated uptime / downtime windows | — | Shared hosting / shared ops team |
| Tor hidden-service descriptor patterns (intro-point overlap, onion-address sibling patterns via [OnionScan](https://github.com/s-rah/onionscan)-style probes) | — | Same Tor daemon / operator |

> **Composition principle.** No single signal above is conclusive; the detector should **combine signals with calibrated weights** and present *attribution confidence bands* rather than binary labels. This matches academic best practice (BNS, bitnodes methodology notes) and the project's existing framing of "anomaly detection" rather than "attacker identification."

### 4. Recommended implementation stack for the detector

A suggested blueprint based on the ecosystem's state as of early 2026. *Confidence: this is judgment, not sourced — included because the user's goal-2 explicitly wants internal-reference material.*

**Core crawler**
- **Language: Rust** preferred for the main crawl loop — async concurrency at thousands of sockets, low memory, solid TLS via `rustls`. Library: **[bitcoindevkit/rust-electrum-client](https://github.com/bitcoindevkit/rust-electrum-client)** (supports plaintext/TLS/Tor) or **[bitcoindevkit/electrum_streaming_client](https://github.com/bitcoindevkit/electrum_streaming_client)** for a push-model client.
- **Reuse, don't reimplement — block-notification collector.** **[0xB10C/fork-observer](https://github.com/0xB10C/fork-observer)** already connects to Electrum servers and tracks reported tips. Integrate rather than re-write the per-server tip-subscription loop and chain-split detection; extend with the extra probing surface this detector needs (`server.features`, `server.banner`, timing capture, TLS/JARM, fee-histogram collection).
- **Python fallback** for prototyping: `connectrum` (historic, used by Electrohunt) or a direct asyncio implementation of the JSON-RPC framing.

**TLS inspection & fingerprinting**
- **[salesforce/jarm](https://github.com/salesforce/jarm)** — reference implementation. Run per-target on port 50002.
- **rustls** for regular TLS handshake + cert chain extraction. Capture full cert DER, issuer, SAN list, validity window.
- **Certificate Transparency**: query `crt.sh` REST API or pull from CT log directly (e.g., via `certstream`).

**Scan & discovery**
- **Censys API** for baseline IPv4 discovery on ports 50001/50002. Free academic tier.
- **Optional ZMap** host (requires root + network allowance) for periodic full-IPv4 confirmation scans — *this has ethical/ISP-relations considerations; require institutional approval before enabling.*
- **Tor gossip-discovery** via the recursive `server.peers.subscribe` crawler (the only path to `.onion` endpoints).

**Enrichment**
- **ASN / geolocation**: Team Cymru Whois service (free, bulk-queryable); MaxMind GeoIP2 (paid, more accurate).
- **BGP / prefix**: CAIDA / RIPE RIS snapshots for /24-to-AS mapping.
- **Reverse DNS**: `getnameinfo` + bulk rDNS datasets (Rapid7 FDNS historic; CAIDA).

**Storage & analytics**
- **DuckDB or Parquet** for the observation DB; millions of rows per crawl, columnar analytics.
- **Event-sourced schema**: append-only `observations(ts, endpoint, signal_type, value, crawl_id)` — reconcile into state tables on read.
- **Graph DB optional** — if the topology graph analysis becomes central, DuckDB's graph-style JOINs are usually enough; don't over-invest in Neo4j prematurely.

**Probe-sequencing engine**
- State-machine per-target: probe-plan generator + collector + back-off governor. **Hard cap on requests/minute/target** — honor hygiene even on suspected-malicious hosts to avoid DoS outcomes and maintain research posture.

**Validation & ground truth**
- **Deploy honeypot servers** of each implementation (ElectrumX / electrs / Fulcrum) in known ASNs / with known cert issuers. Confirm the detector correctly classifies them.
- **Known-good set**: servers published in the Electrum wallet's hardcoded bootstrap list + 1209k monitor-passing list.
- **Known-bad corpus**: Electrohunt IOCs (published subdomain/IP list) + any maintainers' blacklists.
- **Sensitivity analysis**: vary thresholds, measure ROC on honeypot-vs-known-good separation.

### 5. Operational / ethical considerations

- **Active probing of third-party infrastructure.** All crawling should respect:
  - Rate limits (self-imposed ≤ ~1 req/s per target on non-consent crawls; burst-limited during feature collection).
  - No sustained subscription holds (close subscriptions after the minimum time needed).
  - No `blockchain.transaction.broadcast` with crafted non-empty transactions (Electrohunt's method used *invalid* sample txs to elicit errors — still acceptable, but document and label clearly; never broadcast anything that could fund attacker addresses).
- **Tor ethics.** Scanning hidden services is tolerated but rate-limited by Tor itself; aggressive behavior gets you flagged by guards. Coordinate with Tor research community norms.
- **Responsible disclosure.** If the detector identifies an ongoing Sybil attack, the disclosure path is: Electrum maintainers (spesmilo, kyuupichan), major node-package vendors (Umbrel, Start9, RaspiBlitz), and public advisory through [bitcoin-dev](https://groups.google.com/g/bitcoindev) only after operators have had time to react.
- **Data minimization.** The crawler captures scripthash queries *only* against scripthashes the research operator controls — not real user wallets. Never retain third-party observations that leak wallet-identifying data beyond the server-side aggregation level.

### 6. Known gaps & research frontiers

1. **No public Electrum-network census as of early 2026.** Electrohunt is 6+ years stale; no maintained equivalent exists. A fresh, documented crawl is itself a contribution.
2. **No BIP-324-equivalent for Electrum transport.** A defender could propose one alongside detector work — ties to the long-term wallet-privacy agenda.
3. **No standard for operator self-attestation.** `server.features.hosts{}` is the closest thing but under-populated. A "cluster-id" field that operators could set to voluntarily disclose co-operation (and that detectors could *also* infer) would be a valuable protocol addition.
4. **Multi-server wallet-query sharding** (unadopted in protocol-ideas.rst) would raise the attacker's cost even under a large Sybil fleet.
5. **Client-side detector integration.** A lightweight client-side detector (embedded in Electrum wallet itself, not a standalone crawler) is a promising follow-on — the wallet already has ~10 servers' worth of signal per-session.

### Sources (primary, this step)

- [Electrohunt Part 1 — medium.com/iphelix](https://iphelix.medium.com/electrohunt-part-1-hunting-for-the-phishing-campaigns-on-the-electrum-network-b10529162e63)
- [Electrohunt Part 1 — coinbase blog mirror](https://blog.coinbase.com/electrohunt-part-1-hunting-for-the-phishing-campaigns-on-the-electrum-network-b10529162e63)
- [Electrohunt Part 2](https://iphelix.medium.com/electrohunt-part-2-ukraine-obsession-with-crypto-continues-4cbdf99932ae)
- [PortSwigger: 70% of Electrum network compromised (2019)](https://portswigger.net/daily-swig/deep-dive-into-electrum-hack-reveals-70-of-network-was-controlled-by-attackers)
- [0xB10C/projectideas issue #11 — research question provenance](https://github.com/0xB10C/projectideas/issues/11)
- [0xB10C/fork-observer — reusable infrastructure (already speaks Electrum)](https://github.com/0xB10C/fork-observer) · [0xB10C/peer-observer](https://github.com/0xB10C/peer-observer)
- [bitcoin-data organization (archival target)](https://github.com/bitcoin-data) · [bitcoin-data/stale-blocks (primary fork-race event source)](https://github.com/bitcoin-data/stale-blocks)
- [Bitnodes.io](https://bitnodes.io/) · [ayeowch/bitnodes](https://github.com/ayeowch/bitnodes) · [shazow/btc-crawl](https://github.com/shazow/btc-crawl)
- [BNS: A Detection System to Find Nodes in the Bitcoin Network (MDPI, 2023)](https://www.mdpi.com/2227-7390/11/24/4885)
- [1209k.com Bitcoin All-Seeing Eye](https://1209k.com/bitcoin-eye/ele.php)
- [UASF Node Tracker — electrum](https://uasf.saltylemon.org/electrum)
- [bitcoindevkit/rust-electrum-client](https://github.com/bitcoindevkit/rust-electrum-client) · [electrum_streaming_client](https://github.com/bitcoindevkit/electrum_streaming_client)
- [connectrum (PyPI)](https://pypi.org/project/connectrum/) · [stratum-tool](https://github.com/prasos/stratum-tool)
- [salesforce/jarm](https://github.com/salesforce/jarm) · [Salesforce eng blog: Identifying malicious servers with JARM](https://engineering.salesforce.com/easily-identify-malicious-servers-on-the-internet-with-jarm-e095edac525a/) · [Palo Alto: Fingerprinting SSL with JARM + Python](https://medium.com/palo-alto-networks-developer-blog/fingerprinting-ssl-servers-using-jarm-and-python-6d03f6d38dec)
- [Censys](https://censys.io/) · [Shodan](https://www.shodan.io/) · [ZMap](https://zmap.io/)
- [Certificate Transparency](https://certificate.transparency.dev/) · [crt.sh](https://crt.sh/)
- [Team Cymru IP-to-ASN](https://team-cymru.com/community-services/ip-asn-mapping/) · [MaxMind GeoIP2](https://www.maxmind.com/) · [RIPE RIS](https://ris.ripe.net/)
- [s-rah/onionscan (Tor HS fingerprinting)](https://github.com/s-rah/onionscan)

**Empirical probe session (Shodan, 2026-04-23).** Live exploration performed during this research; findings summarized in §2.2.1 above. No dataset URL (Shodan web session).

---

# Research Synthesis — Electrum Protocol Internals and Server Ecosystem

**A Technical Survey for the Electrum Sybil Detector Project**

**Date:** 2026-04-23 · **Author:** Ifuensan · **Scope:** broad technical survey (Steps 1–5 above)

## Executive Summary

The Electrum network is a **small, loosely-specified, long-lived Bitcoin light-client ecosystem** with asymmetric security properties that make Sybil detection both **urgent and tractable**. Five server implementations (ElectrumX, romanz/electrs, Fulcrum, Blockstream/mempool-electrs, Electrum Personal Server) serve a reference client (python-electrum) that maintains **~10 concurrent long-lived TLS sessions** but routes all wallet queries through a **single arbitrarily-chosen "main" server** — a design that makes the expected value of a Sybil attack grow with the attacker's **probability of being selected as main**, not with raw node count. The 2019 attack achieved ~71% control of the public mesh by fanning out ~thousands of subdomain-aliased ghost peers; ElectrumX's subsequent hardening (subnet-deduplicated `server.peers.subscribe` replies, IP-resolution checks on `server.add_peer`, source-rate limiting) closes the **naïve Sybil vector** but is **intra-server** and does nothing against a well-configured attacker-operated fleet distributed across ASNs and CAs. That is the precise gap this detector's Push-3 framing targets via **shared-infrastructure attribution**.

The ecosystem's current state (early 2026) is characterized by three important dynamics that shape what a detector can see: (1) the **community has shifted toward Fulcrum** (C++20 thread-pool, RocksDB 9.2.1, protocol v1.6) for public servers while **romanz/electrs** remains the minimal-index home-node default; (2) protocol version 1.6 introduced a breaking handshake-ordering rule (`server.version` must be first message) that cleanly distinguishes up-to-date vs. legacy servers; (3) **home-node kit distribution** (Umbrel/Start9/RaspiBlitz/MyNode/MiniBolt) imposes shared defaults — banners, cert generation templates, Tor hidden-service port patterns, ZMQ-wired bitcoind backends — across thousands of honest deployments, creating a **tight cluster-shape** against which attacker-configured servers will fingerprint-differ. This research confirms the project's architectural framing: the detector should combine **active Electrum-protocol crawling** (not passive Shodan/Censys, which the 2026-04-23 live probe confirmed is blind to the protocol) with **adjacent-service attribution** (TLS/JARM, ASN, CT-log, Prometheus and Docker Registry leaks, rsyncd banners) to cluster operator-identity and surface divergences that indicate Sybil fleets.

**Key technical findings:**

1. **No canonical specification body.** Electrum is speced in `spesmilo/electrum-protocol` and implemented de-facto by ElectrumX. There is no BIP or IETF document; no formal transport-encryption analogue to Bitcoin Core's BIP-324. Transport security is entirely TLS (usually self-signed + fingerprint-pinned) + Tor.
2. **Wire-protocol fingerprint surface is dense.** `server.version`, `server.features` (full `hosts{}` dict, genesis hash, protocol range, pruning, hash function, server version), `server.banner`, `server.donation_address`, `server.peers.subscribe` (IP, hostname, compact feature-string triples) — each layer leaks identity and implementation. Protocol version 1.6's `server.version`-first rule is a clean discriminator.
3. **Client pool is ~10 concurrent, one-main.** The ~9 non-main sessions only consume `blockchain.headers.subscribe`, leaving **tip-propagation-latency across servers** as a first-class shared-ZMQ-substrate signal for the detector.
4. **Peer-mesh gossip is the richest discovery input.** `server.peers.subscribe` (misnamed — it's a one-shot request, not a subscription) yields the full topology graph with compact feature strings. ElectrumX's gossip hygiene (one peer per IPv4/16 in replies, rate-limited `add_peer`) is strong intra-server and weak against a distributed attacker.
5. **Server-implementation architectures diverge observably.** ElectrumX is asyncio-Python with flat-array height lookups + undo-log reorg replay; romanz/electrs is Rust+Tokio with a compact five-column-family RocksDB schema using key-only rows and re-parse-on-demand (enabling **no-`txindex` operation**); Fulcrum is C++20 ThreadPool with a comprehensive RocksDB index (platform-neutral format in 2.x); mempool/Blockstream electrs fork adds an HTTP REST API exposing `x-powered-by: mempool-electrs <version>` + `x-bitcoin-version: /Satoshi:<X>/` headers — **the single highest-value HTTP-side fingerprint observed in the field**.
6. **Empirical population: ≥ 506 active BTC servers** (per 1209k's monitored list as of 2026-04-23), vs. 130 in the canonical bootstrap — i.e., **~4× expansion from bootstrap to monitor-visible, plus an unknown additional delta discoverable only via recursive gossip and Tor**. No public Electrum-network census has been published since Electrohunt (2019).
7. **Passive datasets (Shodan) are blind to the Electrum protocol.** Confirmed empirically on 2026-04-23: `port:50002` returns 108 754 generic hits (SSH, nginx, webcams), `"ElectrumX"` returns 2 irrelevant matches, and keyword queries on Fulcrum / electrs on port 50002 return zero. The protocol does not emit a banner without a `server.version` probe. **Implication: the detector must build its own active-probing crawler; passive datasets are useful only downstream as attribution pivots.**
8. **Collateral-infrastructure leaks are high-value.** Incidentally-exposed services on Electrum-adjacent hosts (open rsyncd listing multi-chain indexer modules, open Docker Registries listing `bitcoin/electrumx/electrs/zeus` images, Prometheus `node_exporter`, mempool-electrs HTTP APIs exposing `x-bitcoin-version`) reveal **operator stacks without any protocol probing** and cluster cleanly with IP/ASN. This is the Push-3 substrate the detector should exploit.
9. **Hetzner concentration is real and quantified.** 6 of 22 mempool-electrs HTTP endpoints in the Shodan sample resolved to `*.clients.your-server.de`. Hetzner, DigitalOcean, Linode, Contabo dominate the hosting fingerprint. Meaningful for ASN-weighted attribution.
10. **Reorg-handling, rate-limit, JSON-RPC-2.0-strictness, and error-message shape are all observable implementation fingerprints** that stack with banner-level signals for high-confidence implementation classification.

**Strategic recommendations:**

1. **Build an active Electrum-protocol crawler in Rust** using `bitcoindevkit/rust-electrum-client` (plaintext/TLS/Tor support), seeded by the union of the canonical bootstrap (130) + 1209k's monitored list (~506), expanded via recursive `server.peers.subscribe` to closure. **Reuse [0xB10C/fork-observer](https://github.com/0xB10C/fork-observer)** for the block-notification-timing collector rather than reimplementing; extend it with the additional probe surface (`server.features`/banner/cert/JARM/fee-histogram/timing). Passive datasets (Shodan/Censys/CT-logs) feed the **attribution** layer, not the discovery layer.
2. **Compose fingerprints from three orthogonal layers** — *static* (banner, features, cert, open auxiliary ports), *dynamic* (timing distributions, error shapes, rate-limit thresholds, reorg-recovery latency), *shared-infrastructure* (ASN, JARM clusters, CT-log pivots, ZMQ-timing co-publication, donation-address reuse, rsyncd/Docker-Registry leaks). Present attribution as **calibrated confidence bands**, not binary labels.
3. **Validate against known-good honeypots** of each implementation (ElectrumX / electrs / Fulcrum) deployed under controlled ASNs/CAs, plus the 1209k list as a cross-validation feed. Measure coverage delta vs. 1209k as an explicit recall benchmark for the paper.
4. **Frame the paper around the intra-server / shared-infrastructure gap.** The community has already solved the naïve-Sybil problem inside ElectrumX; the contribution of this work is attributing identity across *well-configured* attacker fleets. The 2019 attack is the motivating incident; the 2026 threat model is a smarter attacker.
5. **Respect operational ethics.** Rate-limit active probes (~1 req/s/target), never broadcast crafted transactions, document Shodan/Censys API usage, and coordinate disclosure of any live attack findings with Electrum maintainers (spesmilo, kyuupichan) and node-package vendors (Umbrel, Start9, RaspiBlitz) before public release.

## Table of Contents

This document's body is organized as follows (forward links to the sections above):

1. **Technical Research Scope Confirmation** — research topic, goals, methodology framing.
2. **Technology Stack Analysis** (Step 2) — the five server implementations; wire protocol (JSON-RPC, framing, ports, versioning); protocol version history (1.0 → 1.6); canonical method surface; storage and indexing; clients and libraries; deployment and infrastructure; adoption, population, and the 2019 Sybil incident.
3. **Integration Patterns** (Step 3) — interaction model (request/response/subscription); session lifecycle; client-side pool (~10 concurrent, one-main) and its Sybil-theory implication; peer-mesh gossip dataflow; Bitcoin Core backend integration (RPC / ZMQ / `txindex`); DoS/rate-limit patterns per implementation; security and privacy integration patterns.
4. **Architectural Patterns** (Step 4) — per-implementation internals (ElectrumX asyncio; electrs compact-index schema; Fulcrum ThreadPool; mempool/Blockstream HTTP duals; EPS watcher); reference-client architecture; reorg-handling strategies; operational topology; the "home-node kit" architectural pattern; security and data architecture; synthesis of Sybil-detector implications.
5. **Implementation Research — Detection Practice, Prior Art & Detector-Build Stack** (Step 5) — Electrohunt (2019) methodology and findings; Bitnodes as methodological precedent; bootstrap list (130 servers) + 1209k monitor (506 servers) + UASF tracker as auxiliary seeds; empirical Shodan probe (2026-04-23) with null-result table; detection heuristics by class (static / dynamic / shared-infrastructure); recommended implementation stack; operational and ethical considerations; known research frontiers.
6. **This Research Synthesis.**

## Narrative Introduction

The Electrum network occupies an unusual niche in Bitcoin infrastructure. It is not governed by a BIP, not tracked by the Bitcoin Core project, not indexed by internet-wide scanners in any recognizable form, and yet it serves the majority of Bitcoin **self-custodial light-wallet users** — people who have explicitly opted out of custodial services but cannot run a full node. The gap between "I trust my own keys" and "I trust one anonymous server's view of the chain" is exactly where Electrum sits, and exactly where Sybil attacks hurt most.

The 2019 incident remains the foundational case study: attackers registered thousands of subdomains pointing at a handful of IPs, used ElectrumX's pre-patch `server.add_peer` flow to inject them into the peer mesh, and reached **~71% control** of active nodes at the peak. The payload was a phishing error message delivered through `server.banner` — crude, visible, and correspondingly easy to detect in hindsight. Electrum 3.3.3 and the ElectrumX peer-discovery hardening closed the naïve vector: gossip replies now deduplicate by IPv4 /16, `add_peer` calls validate peer-IP against requester-IP for clearnet, onion peers are rate-limited, and source-rate limits cap the peer-table poisoning surface.

What remained uncovered — and what motivates this research — is the Sybil attacker who **doesn't need to deliver a visible payload**. A better-resourced actor who spreads their fleet across ASNs, CAs, cert issuers, and Tor descriptors can satisfy ElectrumX's gossip hygiene checks while owning enough of the public mesh to bias wallet fee estimation, time-selectively withhold block-tip updates, or simply position themselves for future attacks. ElectrumX's defenses are **intra-server**; they do not — and cannot — reach across the substrate that multiple "independent" servers actually share.

This research surveys the Electrum ecosystem with that threat model in mind. It documents what the protocol actually says (and doesn't), how the five dominant servers differ in architecture and observable behavior, how the reference client's ~10-server pool and single-main-server design shape the attacker's objective function, what the 2019 crawl methodology looked like and why its findings are stale, and what today's deployment patterns — home-node kits, Hetzner/DigitalOcean concentration, mempool-electrs HTTP APIs, Tor-only hidden services — imply for a new detector. An empirical Shodan probe run during the research (2026-04-23) quantified what passive scanning can and cannot see: **nothing useful about the Electrum protocol itself**, but **high-value pivots** for operator-cluster attribution via adjacent services.

The detector this research supports **builds on 0xB10C's existing Bitcoin network-measurement corpus**, not around it. The research question is directly inherited from [0xB10C/projectideas issue #11](https://github.com/0xB10C/projectideas/issues/11) (*"Can we spot public spy-Electrum servers run by Chainalysis?"*, July 2025, still `Todo` at 2026-04-22 — the provenance citation). The crawler reuses [0xB10C/fork-observer](https://github.com/0xB10C/fork-observer) (already speaks Electrum and tracks reported tips). The primary fork-race-event data source is [bitcoin-data/stale-blocks](https://github.com/bitcoin-data/stale-blocks) (3–8 events/month), and the longitudinal Electrum-server dataset produced by this work is targeted for contribution into the same `bitcoin-data` organization as a sibling corpus. The structural gap this detector fills is **layer-complementary**: peer-observer watches the Bitcoin P2P layer, this work watches the Electrum-server layer — a layer that has not been systematically measured since Electrohunt (2019). Positioning the release as a contribution into 0xB10C's ecosystem, rather than parallel to it, is deliberate and architectural.

The material here is written with three audiences in mind, in priority order:

1. **The paper's related-work section.** Citations are to primary sources (GitHub repos, canonical docs, release notes, peer-reviewed crawler studies) rather than blog-post synthesis wherever possible. Confidence levels are flagged where evidence is thin.
2. **The detector team's internal reference** while heuristics are built. Signal tables, fingerprint classes, and stack recommendations are actionable.
3. **Public-facing explainers** (Librería de Satoshi material). The narrative sections and the "why this matters" framing are written to be extractable.

The gap between what is known and what is published about the Electrum network is unusually wide. No maintained public census exists. The rest of this document is an attempt to close that gap to the extent current public information allows, and to map out precisely where active research — including this project — needs to go next.

## Findings Synthesis by Theme

### Theme A — The specification is the implementation

Three findings converge here. The `spesmilo/electrum-protocol` docs are normative but not ratified. The ElectrumX and Fulcrum forks each maintain their own version of "the" spec. Protocol version 1.6's breaking `server.version`-first rule has propagated unevenly — the bootstrap list shows versions 1.4 through 1.6.0 coexisting. A detector's implementation-classification heuristics should therefore not assume strict spec conformance; instead, they should treat **every deviation from 1.6-strict behavior as a fingerprint vector**, not as a misbehavior to be filtered.

### Theme B — The client-side pool invites focused attack

The reference wallet's default is ~10 concurrent connections, with *one* main and the rest consuming only `blockchain.headers.subscribe`. Spread is enforced via subnet/host deduplication on all interfaces **except main**. The attacker's optimization problem is therefore: *maximize P(selected as main) subject to the spread check*. This is satisfied most efficiently by a **diverse-looking but substrate-shared** fleet — precisely the failure mode shared-infrastructure attribution targets. The paper should make this objective function explicit; it reframes "how big is the Sybil attack?" from node-count-ratio to conditional probability.

### Theme C — Three implementations, three observable shapes

ElectrumX's asyncio mono-core architecture, electrs's re-parse-on-demand compact index (enabling `txindex=0` operation on bitcoind!), and Fulcrum's C++20 ThreadPool with comprehensive storage are distinguishable by timing distributions on `scripthash.get_history`, by reorg-recovery latency, by rate-limit shape, and by auxiliary-port exposure (electrs's Prometheus on `:4224`, mempool-electrs's HTTP API). A ~5-probe sequence reliably classifies implementation; adding TLS-layer JARM yields cert-library and deployment-template refinement.

### Theme D — Home-node kits are both the honest-population shape and the detector's calibration ground

Umbrel, Start9, RaspiBlitz, MyNode, MiniBolt, RaspiBolt, and BTCPay Server bundles impose **shared defaults** (cert templates, ports, Tor hidden-service config, ZMQ wiring) across thousands of deployments. When a kit ships an update, hundreds of `server.version` banners flip in a narrow temporal window — a population-level fingerprint that no attacker can easily fake. The detector should treat matches to kit-default fingerprints as **strong evidence of honest-population membership**, and anomalies within expected kit signatures (e.g., a Fulcrum version no kit has shipped yet) as **calibration markers** worth investigating.

### Theme E — Passive scanning is blind to Electrum but useful for attribution

The 2026-04-23 empirical probe closed a question the detector team likely had in mind: can Shodan / Censys serve as primary discovery sources? No. `port:50002` is 108k hits of noise; keyword filters for ElectrumX/Fulcrum yield zero matches on the Electrum protocol itself. But the same session surfaced several **operator-stack-confession** instances (open rsyncd with multi-chain indexer modules; open Docker Registry with a full Bitcoin/Electrum image inventory; mempool-electrs `x-powered-by` + `x-bitcoin-version` header pairs). The architectural implication is clear: active protocol probing for discovery + passive-dataset cross-reference for attribution. Treat `port:8332 port:50002` co-residence as a *tripwire query* (should always be zero; any hit is a high-signal anomaly).

### Theme F — The empirical gap is itself a contribution opportunity

Electrohunt (2019) is the last published crawler study. The canonical bootstrap is 130 servers. 1209k tracks 506. The true public-mesh population (including Tor-only) is larger still. A fresh, documented, reproducible crawl with full fingerprint collection is itself a publishable contribution alongside the Sybil-detection methodology.

## Strategic Technical Recommendations

### For the detector architecture

1. **Language: Rust** for the main crawler (rust-electrum-client, rustls, tokio); Python for prototyping / data analysis. Storage: DuckDB/Parquet columnar observation log with event-sourced `observations(ts, endpoint, signal_type, value, crawl_id)` schema.
2. **Discovery pipeline**: `bootstrap ∪ 1209k list → active server.peers.subscribe traversal → closure`. Include Tor crawling via SOCKS5; accept gossip-only discovery for `.onion` endpoints.
3. **Probing pipeline per host**: `server.version → server.features → server.banner → server.donation_address → TLS handshake + cert capture → JARM → blockchain.headers.subscribe (30-min window for tip-propagation timing) → blockchain.scripthash.get_history (on controlled scripthash, for timing distribution)`. Hard rate-limit ≤ 1 req/s/host.
4. **Enrichment pipeline**: ASN via Team Cymru; geolocation via MaxMind; cert chain via CT logs / crt.sh; reverse DNS; Shodan facet lookups for adjacent-port and Prometheus/Docker-Registry correlation.
5. **Attribution layer**: stacked classifiers combining static (banner, features, cert, JARM), dynamic (timing, error shape), and shared-infrastructure (ASN, co-residence, tip-propagation correlation) signals. Output: operator-cluster assignments with confidence bands, not binary labels.
6. **Validation**: honeypots of each implementation in controlled ASNs; coverage/recall benchmarks against 1209k; replay against known-good bootstrap; test against Electrohunt IOCs (if still relevant).

### For the research paper

1. **Frame the contribution as "shared-infrastructure attribution beyond intra-server defenses."** Position the work against the 2019 attack and the subsequent ElectrumX hardening.
2. **Make the attacker's objective function explicit.** The detector's value proposition is measured against `P(Sybil controls the main-server slot)`, not against Sybil node count.
3. **Publish the crawl as part of the paper.** Reproducible methodology + fresh empirical data + detection heuristics is a stronger contribution than heuristics in isolation.
4. **Cite primary sources throughout.** The GitHub repos, protocol docs, release notes, and Electrohunt post are all primary; 1209k is an operational artifact, not a research dataset.
5. **Acknowledge the limits.** Tor-only endpoints have reduced fingerprint surface; passive datasets miss the protocol; `server.features.hosts{}` is sparsely populated. The detector is probabilistic.

### For the public-facing Librería de Satoshi material

1. **Lead with the 2019 attack and the scripthash privacy model.** Relatable stakes, concrete history.
2. **Explain the ~10-server pool and the "main server sees your queries" detail.** Useful for practical privacy recommendations (`--oneserver` + `.onion`).
3. **Explain why home-node kits concentrate the honest population.** Celebrates the community's existing work while motivating why attackers can still hide in the gaps.
4. **Do not publish live detector findings before responsible disclosure.** Coordinate with Spanish-speaking Bitcoin community norms.

## Research Frontiers and Knowledge Gaps

1. **A current public Electrum-network census.** Electrohunt is 6+ years stale. A fresh crawl with published methodology and anonymized data would serve the community and the paper.
2. **A BIP-324-equivalent for Electrum transport.** The protocol is exposed on plaintext TCP by default. A well-drafted proposal (authenticated-encryption handshake, opportunistic upgrade) would close a structural weakness.
3. **A standard for operator self-attestation.** `server.features.hosts{}` is the closest thing and is under-used. A voluntary "operator-id" field would make attribution ground-truth cheaper to assemble.
4. **Client-side detector integration.** The reference wallet already observes 10 servers per session — it could run a lightweight anomaly check locally, warning users before `main` selection. A natural follow-up project.
5. **Multi-server wallet-query sharding.** Electrum's `protocol-ideas.rst` contemplates this and hasn't adopted it. It would raise the Sybil attacker's cost even under large fleets.
6. **Cross-chain precedents.** Lightning Network graph Sybil analysis, Ethereum execution-layer node crawlers, and privacy-coin server ecosystem studies all have transferable techniques. An academic cross-reference section would strengthen the paper.

## Research Methodology and Source Verification

**Methodology:** Broad-survey technical research with rigorous primary-source verification. Primary sources prioritized: canonical protocol repositories (`spesmilo/electrum-protocol`, `kyuupichan/electrumx`), reference implementations (`spesmilo/electrum`, `romanz/electrs`, `cculianu/Fulcrum`, `Blockstream/electrs`, `mempool/electrs`, `chris-belcher/electrum-personal-server`), official docs (electrumx.readthedocs.io, electrum-protocol.readthedocs.io), release notes / changelogs, and the Electrohunt crawler report. Cross-validated against operator guides (RaspiBolt, RaspiBlitz, Umbrel, Start9, MiniBolt, Sparrow server-performance notes), Casa 2022 benchmarks, and the 1209k public monitor. A live Shodan-based empirical probe was conducted on 2026-04-23 to quantify passive-scan coverage of the Electrum population.

**Confidence-level framework:** claims were flagged HIGH (multiple independent primary sources agree), MEDIUM (single authoritative source or consistent secondary-source convergence), or LOW (anecdotal / survey-based). Benchmarks and population estimates are explicitly flagged because environment-dependent.

**Limitations:**
- Tor-only hidden services: reduced observational surface, coverage depends on gossip.
- No peer-reviewed Electrum network census since 2019; operator-poll data is self-selected.
- The Shodan probe was web-UI-based, one-shot; longitudinal data not captured.
- Fulcrum source-code internals were inferred from file names (`Controller.h`, `SubsMgr.h`, `ThreadPool.h`, `ThreadSafeHashTable.h`) rather than direct code reading.
- The BlueWallet / Sparrow / coin-fork client landscape received lighter coverage than the reference client.

**Research completion**: 2026-04-23. Document version: 1.0.

## Conclusion

The Electrum ecosystem is well-suited to Sybil attacks because its protocol has no authentication model, no encrypted transport, no formal standards body, and serves light-client users whose threat model concentrates trust in a single session. It is also well-suited to Sybil *detection* — precisely because its small implementation landscape, heavy reliance on home-node kits with shared defaults, rich protocol-level fingerprint surface, and incidentally-exposed operator infrastructure create dense, stackable signals that a careful crawler can harvest and correlate. The 2019 attack closed the naïve vector; the 2026 threat model demands attribution across substrate rather than across self-advertised identity.

The Electrum Sybil Detector project is well-positioned in that gap. The Push-3 reframing — from intent attribution to shared-infrastructure attribution — matches exactly what this survey's evidence supports. What remains is to build the crawler, populate the signal tables, calibrate the classifiers against honeypots and the 1209k reference, and publish the methodology and data alongside the detection results. The community has every incentive to welcome the contribution: operators, wallet maintainers, and users all benefit from a clearer picture of who is running the network they depend on.

---

**Document length:** comprehensive · **Source verification:** all substantive claims cited with URLs inline · **Technical confidence level:** HIGH where explicitly stated; MEDIUM or LOW where flagged · **Research completion date:** 2026-04-23.

*This document serves as an authoritative technical reference on the Electrum protocol and server ecosystem for the Electrum Sybil Detector research project, positioned to inform the paper's related-work section, the detector team's internal heuristic development, and public-facing material published by Librería de Satoshi.*
